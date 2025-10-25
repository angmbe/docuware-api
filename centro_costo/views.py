from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CentroCosto
from .serializers import CentroCostoSerializer

class CentroCostoListView(APIView):
    def get(self, request):
        centros = CentroCosto.objects.all().order_by('centrocodigo')
        serializer = CentroCostoSerializer(centros, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
