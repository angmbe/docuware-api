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
    documentserial = serializers.SerializerMethodField()
    documentnumber = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = "__all__"
    def get_documentserial(self, obj):
        return obj.documentserial or ""

    def get_documentnumber(self, obj):
        return obj.documentnumber or ""
