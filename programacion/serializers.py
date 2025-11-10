from rest_framework import serializers
from .models import Vehiculo, Conductor, ProgramacionDiaria

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'


class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = '__all__'


class ProgramacionDiariaSerializer(serializers.ModelSerializer):
    vehiculo = VehiculoSerializer(read_only=True)
    conductor = ConductorSerializer(read_only=True)

    idvehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(),
        source='vehiculo',
        write_only=True
    )
    idconductor = serializers.PrimaryKeyRelatedField(
        queryset=Conductor.objects.all(),
        source='conductor',
        write_only=True
    )

    class Meta:
        model = ProgramacionDiaria
        fields = [
            'programacionid',
            'programacionfecha',
            'vehiculo',
            'conductor',
            'idvehiculo',
            'idconductor'
        ]
