import json
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView

from utils.responses import standard_response

from .models import Expediente, ExpedienteDocumento
from .serializers import (
    ExpedienteDocumentoSerializer,
    ExpedienteDocumentoUploadSerializer,
    ExpedienteSerializer,
    ExpedienteUploadSerializer,
    validate_pdf_uploaded_file,
)


def build_expediente_storage_path(current_date, expediente_folder_name):
    return (
        Path("expedientes")
        / current_date.strftime("%Y")
        / current_date.strftime("%m")
        / expediente_folder_name
    )


def store_expediente_file(uploaded_file, expediente_folder_name):
    current_date = timezone.localtime()
    relative_dir = build_expediente_storage_path(current_date, expediente_folder_name)
    target_dir = Path(settings.MEDIA_ROOT) / relative_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    storage = FileSystemStorage(location=target_dir)
    stored_file_name = storage.save(uploaded_file.name, uploaded_file)
    stored_relative_path = (relative_dir / stored_file_name).as_posix()
    return stored_file_name, stored_relative_path


def parse_expediente_documentos(raw_documentos):
    if raw_documentos in (None, "", []):
        return []

    if isinstance(raw_documentos, str):
        try:
            documentos = json.loads(raw_documentos)
        except json.JSONDecodeError as exc:
            raise ValueError("El campo expediente_documentos debe ser un JSON valido.") from exc
    else:
        documentos = raw_documentos

    if not isinstance(documentos, list):
        raise ValueError("El campo expediente_documentos debe ser una lista.")

    return documentos


class ExpedienteUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ExpedienteUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Error al cargar el expediente",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        expedienteid = serializer.validated_data["expedienteid"]
        uploaded_file = serializer.validated_data["file"]
        stored_file_name, stored_relative_path = store_expediente_file(
            uploaded_file,
            expedienteid,
        )

        return standard_response(
            success=True,
            message="PDF cargado correctamente",
            data={
                "expedienteid": expedienteid,
                "file_name": stored_file_name,
                "relative_path": stored_relative_path,
            },
            status_code=status.HTTP_201_CREATED,
        )


class ExpedienteDocumentoUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, expedienteid):
        try:
            expediente = Expediente.objects.get(expedienteid=expedienteid)
        except Expediente.DoesNotExist:
            return standard_response(
                success=False,
                message="Expediente no encontrado",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = ExpedienteDocumentoUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Error al cargar el documento del expediente",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = serializer.validated_data["file"]
        stored_file_name, stored_relative_path = store_expediente_file(
            uploaded_file,
            str(expediente.expedienteid),
        )

        expediente_documento = ExpedienteDocumento.objects.create(
            expedienteid=expediente,
            tipodocumentoid=serializer.validated_data["tipodocumentoid"],
            filename=stored_file_name,
            filepath=stored_relative_path,
            estado=serializer.validated_data.get("estado", True),
            createdby=serializer.validated_data.get("createdby"),
        )

        response_serializer = ExpedienteDocumentoSerializer(expediente_documento)
        return standard_response(
            success=True,
            message="Documento del expediente cargado correctamente",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class ExpedienteListCreateView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        expedienteid = request.query_params.get("expedienteid")
        expedientes = Expediente.objects.select_related(
            "facturaid",
            "ordencompraid",
        ).prefetch_related("expediente_documentos")

        if expedienteid:
            expedientes = expedientes.filter(expedienteid=expedienteid)

        serializer = ExpedienteSerializer(expedientes.order_by("-expedienteid"), many=True)
        return standard_response(
            success=True,
            message="Expedientes obtenidos correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.FILES:
            return self._create_expediente_with_files(request)

        serializer = ExpedienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                success=True,
                message="Expediente creado correctamente",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )

        return standard_response(
            success=False,
            message="Error al crear el expediente",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def _create_expediente_with_files(self, request):
        try:
            documentos_data = parse_expediente_documentos(
                request.data.get("expediente_documentos")
            )
        except ValueError as exc:
            return standard_response(
                success=False,
                message="Error al crear el expediente",
                data={"expediente_documentos": [str(exc)]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        expediente_payload = {
            "facturaid": request.data.get("facturaid"),
            "ordencompraid": request.data.get("ordencompraid"),
            "estado": request.data.get("estado"),
            "createdby": request.data.get("createdby"),
            "updatedby": request.data.get("updatedby"),
        }
        expediente_payload = {
            key: value for key, value in expediente_payload.items() if value not in (None, "")
        }

        serializer = ExpedienteSerializer(data=expediente_payload)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Error al crear el expediente",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                expediente = serializer.save()

                for documento in documentos_data:
                    file_field = documento.get("file_field")
                    if file_field:
                        uploaded_file = request.FILES.get(file_field)
                        if not uploaded_file:
                            raise ValueError(
                                f"No se encontro el archivo para el campo '{file_field}'."
                            )
                        validate_pdf_uploaded_file(uploaded_file)
                        stored_file_name, stored_relative_path = store_expediente_file(
                            uploaded_file,
                            str(expediente.expedienteid),
                        )
                        ExpedienteDocumento.objects.create(
                            expedienteid=expediente,
                            tipodocumentoid=documento.get("tipodocumentoid"),
                            filename=stored_file_name,
                            filepath=stored_relative_path,
                            estado=documento.get("estado", True),
                            createdby=documento.get("createdby"),
                        )
                    else:
                        ExpedienteDocumento.objects.create(
                            expedienteid=expediente,
                            tipodocumentoid=documento.get("tipodocumentoid"),
                            filename=documento.get("filename"),
                            filepath=documento.get("filepath"),
                            estado=documento.get("estado", True),
                            createdby=documento.get("createdby"),
                            updatedby=documento.get("updatedby"),
                            updatedat=documento.get("updatedat"),
                        )
        except ValueError as exc:
            return standard_response(
                success=False,
                message="Error al crear el expediente",
                data={"expediente_documentos": [str(exc)]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return standard_response(
                success=False,
                message="Error al crear el expediente",
                data={"detail": [str(exc)]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        expediente = Expediente.objects.select_related(
            "facturaid",
            "ordencompraid",
        ).prefetch_related("expediente_documentos").get(pk=expediente.pk)

        return standard_response(
            success=True,
            message="Expediente creado correctamente",
            data=ExpedienteSerializer(expediente).data,
            status_code=status.HTTP_201_CREATED,
        )
