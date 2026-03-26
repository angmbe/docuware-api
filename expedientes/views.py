from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from utils.responses import standard_response

from .serializers import ExpedienteUploadSerializer


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
        current_date = timezone.localtime()

        relative_dir = Path("expedientes") / current_date.strftime("%Y") / current_date.strftime("%m") / expedienteid
        target_dir = Path(settings.MEDIA_ROOT) / relative_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        storage = FileSystemStorage(location=target_dir)
        stored_file_name = storage.save(uploaded_file.name, uploaded_file)
        stored_relative_path = (relative_dir / stored_file_name).as_posix()

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
