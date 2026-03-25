from rest_framework import status
from rest_framework.views import APIView

from utils.responses import standard_response

from .models import Proveedor
from .serializers import ProveedorSerializer


class ProveedorListCreateView(APIView):
    def get(self, request):
        supplierno = request.query_params.get("supplierno")
        proveedores = Proveedor.objects.select_related("bank1", "bank2")

        if supplierno and supplierno.strip():
            proveedores = proveedores.filter(supplierno__iexact=supplierno.strip())

        serializer = ProveedorSerializer(proveedores.order_by("supplierid"), many=True)
        return standard_response(
            success=True,
            message="Proveedores obtenidos correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        supplierid = request.data.get("supplierid")

        if supplierid:
            try:
                proveedor = Proveedor.objects.get(supplierid=supplierid)
            except Proveedor.DoesNotExist:
                return standard_response(
                    success=False,
                    message="Proveedor no encontrado",
                    data=None,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            serializer = ProveedorSerializer(
                proveedor,
                data=request.data,
                partial=True,
            )
            success_message = "Proveedor actualizado correctamente"
            success_status = status.HTTP_200_OK
        else:
            serializer = ProveedorSerializer(data=request.data)
            success_message = "Proveedor creado correctamente"
            success_status = status.HTTP_201_CREATED

        if serializer.is_valid():
            serializer.save()
            return standard_response(
                success=True,
                message=success_message,
                data=serializer.data,
                status_code=success_status,
            )

        return standard_response(
            success=False,
            message="Error al registrar el proveedor",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
