import re

from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from documents.serializers import DocumentSerializer, PurchaseOrderSerializer

from .models import Expediente, ExpedienteDocumento


class BitBooleanField(serializers.Field):
    TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
    FALSE_VALUES = {"0", "false", "f", "no", "n", "off", ""}

    def to_representation(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if isinstance(value, bytes):
            return value not in (b"", b"\x00", b"0")
        if isinstance(value, str):
            return value.strip().lower() in self.TRUE_VALUES
        return False

    def to_internal_value(self, data):
        if isinstance(data, bool):
            return "1" if data else "0"
        if isinstance(data, int):
            return "1" if data == 1 else "0"
        if isinstance(data, bytes):
            return "0" if data in (b"", b"\x00", b"0") else "1"
        if isinstance(data, str):
            value = data.strip().lower()
            if value in self.TRUE_VALUES:
                return "1"
            if value in self.FALSE_VALUES:
                return "0"

        raise serializers.ValidationError("El campo lock_exp debe ser booleano.")


def validate_pdf_uploaded_file(value):
    file_name = value.name.lower()
    content_type = getattr(value, "content_type", "")

    if not file_name.endswith(".pdf") and content_type != "application/pdf":
        raise serializers.ValidationError("Solo se permiten archivos PDF.")

    return value


class ExpedienteUploadSerializer(serializers.Serializer):
    expedienteid = serializers.CharField(max_length=100)
    file = serializers.FileField()

    def validate_expedienteid(self, value):
        expedienteid = value.strip()
        if not expedienteid:
            raise serializers.ValidationError("El campo expedienteid es obligatorio.")
        if not re.match(r"^[A-Za-z0-9_-]+$", expedienteid):
            raise serializers.ValidationError(
                "El expedienteid solo puede contener letras, numeros, guiones y guion bajo."
            )
        return expedienteid

    def validate_file(self, value):
        return validate_pdf_uploaded_file(value)


class ExpedienteDocumentoUploadSerializer(serializers.Serializer):
    tipodocumentoid = serializers.IntegerField()
    file = serializers.FileField()
    estado = serializers.BooleanField(required=False, default=True)
    createdby = serializers.IntegerField(required=False, allow_null=True)

    def validate_file(self, value):
        return validate_pdf_uploaded_file(value)


class ExpedienteDocumentoSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ExpedienteDocumento
        fields = [
            "expedientedocid",
            "expedienteid",
            "tipodocumentoid",
            "filename",
            "filepath",
            "file_url",
            "estado",
            "createdby",
            "createat",
            "updatedby",
            "updatedat",
        ]
        extra_kwargs = {
            "expedientedocid": {"read_only": True},
            "expedienteid": {"read_only": True},
        }

    def get_file_url(self, obj):
        if not obj.filepath:
            return None

        url = default_storage.url(obj.filepath)
        request = self.context.get("request")
        if request and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url


class ExpedienteSerializer(serializers.ModelSerializer):
    expediente_documentos = ExpedienteDocumentoSerializer(many=True, required=False)
    factura = serializers.SerializerMethodField()
    ordencompra = serializers.SerializerMethodField()
    lock_exp = BitBooleanField(required=False, default="0")

    class Meta:
        model = Expediente
        fields = [
            "expedienteid",
            "facturaid",
            "factura",
            "ordencompraid",
            "ordencompra",
            "estado",
            "lock_exp",
            "createdby",
            "createat",
            "updatedby",
            "updatedat",
            "expediente_documentos",
        ]
        read_only_fields = ("expedienteid", "createat", "updatedat")

    def create(self, validated_data):
        documentos_data = validated_data.pop("expediente_documentos", [])
        now = timezone.now()
        validated_data.setdefault("createat", now)
        validated_data.setdefault("lock_exp", "0")

        with transaction.atomic():
            expediente = Expediente.objects.create(**validated_data)
            documentos = []

            for documento_data in documentos_data:
                documento_data.setdefault("createat", now)
                documentos.append(
                    ExpedienteDocumento(
                        expedienteid=expediente,
                        **documento_data,
                    )
                )

            if documentos:
                ExpedienteDocumento.objects.bulk_create(documentos)

        return Expediente.objects.prefetch_related("expediente_documentos").get(
            pk=expediente.pk
        )

    def get_factura(self, obj):
        if not obj.facturaid:
            return None
        return DocumentSerializer(obj.facturaid).data

    def get_ordencompra(self, obj):
        if not obj.ordencompraid:
            return None
        return PurchaseOrderSerializer(obj.ordencompraid).data
