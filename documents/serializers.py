from rest_framework import serializers
from .models import Document, TipoDocumento

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        #fields = "__all__"
        fields = ["tipoid", "tipo"]  # solo los campos que quieres exponer
        
class DocumentSerializer(serializers.ModelSerializer):
    documenttype = TipoDocumentoSerializer(read_only=True)
    class Meta:
        model = Document
        fields = "__all__"
