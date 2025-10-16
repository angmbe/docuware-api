from rest_framework import serializers
from .models import DocumentDetail

class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentDetail
        fields = "__all__"

class DocumentFullSerializer(serializers.Serializer):
    #campos del documento (cabecera)
    suppliernumber = serializers.CharField()
    documentserial = serializers.CharField()
    documentnumber = serializers.CharField()
    documentdate = serializers.DateField(required=False, allow_null=True)
    doctype = serializers.CharField(required=False, allow_null=True)
    currency = serializers.CharField(required=False, allow_null=True)
    totalamount = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    #campos del detalle 
    itemcode = serializers.CharField(required=False, allow_null=True)
    itemdescription = serializers.CharField(required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    unitprice = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    subtotal = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, allow_null=True)
    
