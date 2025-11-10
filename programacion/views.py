from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vehiculo, Conductor, ProgramacionDiaria
from .serializers import VehiculoSerializer, ConductorSerializer, ProgramacionDiariaSerializer

# --- GET Vehículos ---
class VehiculoListView(APIView):
    def get(self, request):
        vehiculos = Vehiculo.objects.all().order_by('no_vehiculo')
        serializer = VehiculoSerializer(vehiculos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- GET Conductores ---
class ConductorListView(APIView):
    def get(self, request):
        conductores = Conductor.objects.all().order_by('conductor_nm')
        serializer = ConductorSerializer(conductores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- Programación diaria ---
class ProgramacionDiariaView(APIView):
    def get(self, request):
        """Obtener todas las programaciones"""
        programaciones = ProgramacionDiaria.objects.select_related('vehiculo', 'conductor').order_by('-programacionfecha')
        serializer = ProgramacionDiariaSerializer(programaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Registrar una nueva programación"""
        serializer = ProgramacionDiariaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """Actualizar parcialmente una programación"""
        programacionid = request.data.get("programacionid", None)
        if not programacionid:
            return Response({"error": "programacionid es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            programacion = ProgramacionDiaria.objects.get(programacionid=programacionid)
        except ProgramacionDiaria.DoesNotExist:
            return Response({"error": "Programación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProgramacionDiariaSerializer(programacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
