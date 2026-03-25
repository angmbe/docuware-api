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
        serializer = ProveedorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                success=True,
                message="Proveedor creado correctamente",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )

        return standard_response(
            success=False,
            message="Error al crear el proveedor",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
