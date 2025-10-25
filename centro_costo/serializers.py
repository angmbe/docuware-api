from rest_framework import serializers
from .models import CentroCosto

class CentroCostoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentroCosto
        fields = '__all__'
