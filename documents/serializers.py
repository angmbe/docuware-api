from rest_framework import serializers
from .models import Document, TipoDocumento

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        #fields = "__all__"
        fields = ["tipoid", "tipo"]  # solo los campos que quieres exponer
        
class DocumentSerializer(serializers.ModelSerializer):
    documenttype = TipoDocumentoSerializer(read_only=True)
    documenttype_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all(),
        source="documenttype",
        write_only=True
    )
    # Evita null y permite postear valores
    documentserial = serializers.CharField(allow_blank=True, required=False)
    documentnumber = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Document
        fields = "__all__"

    def to_representation(self, instance):
        """Evita que se muestre null y en su lugar vacío"""
        data = super().to_representation(instance)
        if data.get("documentserial") is None:
            data["documentserial"] = ""
        if data.get("documentnumber") is None:
            data["documentnumber"] = ""
        return data

