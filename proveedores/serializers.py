from django.utils import timezone
from rest_framework import serializers

from catalogos.models import Catalogo
from catalogos.serializers import CatalogoSerializer

from .models import Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    bank1 = CatalogoSerializer(read_only=True)
    bank1_id = serializers.PrimaryKeyRelatedField(
        queryset=Catalogo.objects.all(),
        source="bank1",
        write_only=True,
        required=False,
        allow_null=True,
    )
    bank2 = CatalogoSerializer(read_only=True)
    bank2_id = serializers.PrimaryKeyRelatedField(
        queryset=Catalogo.objects.all(),
        source="bank2",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Proveedor
        fields = [
            "supplierid",
            "supplierno",
            "suppliername",
            "address",
            "phone",
            "email",
            "bank1",
            "bank1_id",
            "accountno1",
            "bank2",
            "bank2_id",
            "accountno2",
            "createdby",
            "createdat",
            "updatedby",
            "updatedat",
        ]
        read_only_fields = ("supplierid", "createdat", "updatedat")

    def validate_supplierno(self, value):
        if value == "":
            return None
        return value

    def create(self, validated_data):
        now = timezone.now()
        validated_data.setdefault("createdat", now)
        validated_data.setdefault("updatedat", now)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updatedat"] = timezone.now()
        return super().update(instance, validated_data)
