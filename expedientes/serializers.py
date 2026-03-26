import re

from rest_framework import serializers


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
        file_name = value.name.lower()
        content_type = getattr(value, "content_type", "")

        if not file_name.endswith(".pdf") and content_type != "application/pdf":
            raise serializers.ValidationError("Solo se permiten archivos PDF.")

        return value
