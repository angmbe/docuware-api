from rest_framework import status
from rest_framework.views import APIView

from utils.responses import standard_response

from .jobs import get_job, start_documentos_sunat_job
from .services import ApisunatError, get_documentos_sunat, validate_date_range


class GetDocumentosSunatView(APIView):
    def get(self, request):
        fecha_inicio = request.query_params.get("fecha_inicio")
        fecha_fin = request.query_params.get("fecha_fin")
        created_by = request.query_params.get("created_by") or request.query_params.get("createdby")
        async_mode = request.query_params.get("async") or request.query_params.get("async_mode")
        return self._handle_request(fecha_inicio, fecha_fin, created_by, async_mode=async_mode)

    def post(self, request):
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_fin = request.data.get("fecha_fin")
        created_by = request.data.get("created_by") or request.data.get("createdby")
        async_mode = request.data.get("async") or request.data.get("async_mode")
        return self._handle_request(fecha_inicio, fecha_fin, created_by, async_mode=async_mode)

    def _handle_request(self, fecha_inicio, fecha_fin, created_by, async_mode=None):
        if str(async_mode).lower() in {"1", "true", "yes", "si"}:
            try:
                validate_date_range(fecha_inicio, fecha_fin)
            except (TypeError, ValueError) as exc:
                return standard_response(
                    success=False,
                    message=str(exc),
                    data=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            job = start_documentos_sunat_job(fecha_inicio, fecha_fin, created_by=created_by)
            return standard_response(
                success=True,
                message="Consulta SUNAT iniciada en segundo plano",
                data=job,
                status_code=status.HTTP_202_ACCEPTED,
            )

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


class GetDocumentosSunatJobView(APIView):
    def get(self, request, job_id):
        job = get_job(job_id)
        if not job:
            return standard_response(
                success=False,
                message="Trabajo SUNAT no encontrado",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return standard_response(
            success=job.get("status") != "error",
            message=job.get("message") or "Estado de consulta SUNAT",
            data=job,
            status_code=status.HTTP_200_OK,
        )
