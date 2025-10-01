from rest_framework import serializers
from .models import DocumentDetail

class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentDetail
        fields = "__all__"

