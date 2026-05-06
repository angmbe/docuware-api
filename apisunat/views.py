from rest_framework import status
from rest_framework.views import APIView

from utils.responses import standard_response

from .services import ApisunatError, get_documentos_sunat


class GetDocumentosSunatView(APIView):
    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        created_by = request.query_params.get("created_by") or request.query_params.get("createdby")
        return self._handle_request(fecha_inicio, fecha_fin, created_by)

    def post(self, request):
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_fin = request.data.get("fecha_fin")
        created_by = request.data.get("created_by") or request.data.get("createdby")
        return self._handle_request(fecha_inicio, fecha_fin, created_by)

    def _handle_request(self, fecha_inicio, fecha_fin, created_by):
        try:
            data = get_documentos_sunat(fecha_inicio, fecha_fin, created_by=created_by)
        except (TypeError, ValueError) as exc:
            return standard_response(
                success=False,
                message=str(exc),
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except ApisunatError as exc:
            return standard_response(
                success=False,
                message=str(exc),
                data=None,
                status_code=status.HTTP_502_BAD_GATEWAY,
            )

        return standard_response(
            success=True,
            message="Documentos SUNAT obtenidos correctamente",
            data=data,
            status_code=status.HTTP_200_OK,
        )
