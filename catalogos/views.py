from rest_framework import status
from rest_framework.views import APIView

from utils.responses import standard_response

from .models import Catalogo
from .serializers import CatalogoSerializer


class CatalogoListView(APIView):
    def get(self, request):
        tipo_catalogo = request.query_params.get("tipo_catalogo")

        if not tipo_catalogo:
            return standard_response(
                success=False,
                message="El parámetro 'tipo_catalogo' es obligatorio",
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        catalogos = Catalogo.objects.filter(
            tipo_catalogo__iexact=tipo_catalogo.strip()
        ).order_by("codigo")
        serializer = CatalogoSerializer(catalogos, many=True)

        return standard_response(
            success=True,
            message="Catálogo obtenido correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )
