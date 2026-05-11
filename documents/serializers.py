from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from catalogos.serializers import CatalogoSerializer
from centro_costo.models import CentroCosto
from centro_costo.serializers import CentroCostoSerializer
from proveedores.models import Proveedor
from .models import Document, PurchaseOrder, PurchaseOrderDetail, TipoDocumento

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        #fields = "__all__"
        fields = ["tipoid", "tipo"]  # solo los campos que quieres exponer


class PurchaseOrderProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["supplierid", "supplierno", "suppliername"]
        
class DocumentSerializer(serializers.ModelSerializer):
    documenttype = TipoDocumentoSerializer(read_only=True)
    documenttype_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all(),
        source="documenttype",
        write_only=True
    )
    centercost = CentroCostoSerializer(read_only=True)  # 👈 Aquí el cambio importante
    centercost_id = serializers.PrimaryKeyRelatedField(
        queryset=CentroCosto.objects.all(),
        source="centercost",
        write_only=True,
        required=False
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
        if data.get("centrocodigo") is None:
            data["centrocodigo"] = ""
        return data


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderDetail
        fields = "__all__"
        extra_kwargs = {
            "purchaseDetailID": {"read_only": True},
            "purchaseOrderID": {"read_only": True},
        }


class PurchaseOrderSerializer(serializers.ModelSerializer):
    details = PurchaseOrderDetailSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "purchaseOrderID",
            "orderNo",
            "supplierID",
            "documentAssociatedType",
            "documentAssociatedNo",
            "paymentCondition",
            "currency",
            "guideNo",
            "store",
            "purchaseState",
            "tipoorden",
            "signature",
            "signature2",
            "requiredby",
            "createdBy",
            "createAt",
            "updatedBy",
            "updatedAt",
            "details",
        ]
        extra_kwargs = {
            "purchaseOrderID": {"read_only": True},
        }

    def validate_details(self, value):
        if not value:
            raise serializers.ValidationError("Debe enviar al menos un detalle.")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        create_at = validated_data.get("createAt") or timezone.localdate()
        created_by = validated_data.get("createdBy")

        validated_data["createAt"] = create_at

        with transaction.atomic():
            tipoorden = validated_data.get("tipoorden")
            if tipoorden in ["S", "C"]:
                prefix = "OS" if tipoorden == "S" else "OC"
                current_year = str(create_at.year)
                prefix_year = f"{prefix}-{current_year}-"
                
                last_po = PurchaseOrder.objects.filter(
                    orderNo__startswith=prefix_year
                ).order_by("-orderNo").first()

                if last_po and last_po.orderNo:
                    try:
                        last_correlative = int(last_po.orderNo.split("-")[-1])
                        new_correlative = last_correlative + 1
                    except ValueError:
                        new_correlative = 1
                else:
                    new_correlative = 1
                
                validated_data["orderNo"] = f"{prefix_year}{new_correlative:05d}"

            purchase_order = PurchaseOrder.objects.create(**validated_data)
            detail_instances = []

            for detail_data in details_data:
                detail_data.setdefault("createAt", create_at)
                if created_by is not None:
                    detail_data.setdefault("createdBy", created_by)
                detail_instances.append(
                    PurchaseOrderDetail(
                        purchaseOrderID=purchase_order,
                        **detail_data,
                    )
                )

            PurchaseOrderDetail.objects.bulk_create(detail_instances)

        return PurchaseOrder.objects.prefetch_related("details").get(
            pk=purchase_order.pk
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["supplierID"] = (
            PurchaseOrderProveedorSerializer(instance.supplierID).data
            if instance.supplierID
            else None
        )
        data["documentAssociatedType"] = (
            TipoDocumentoSerializer(instance.documentAssociatedType).data
            if instance.documentAssociatedType
            else None
        )
        data["paymentCondition"] = (
            CatalogoSerializer(instance.paymentCondition).data
            if instance.paymentCondition
            else None
        )
        data["currency"] = (
            CatalogoSerializer(instance.currency).data
            if instance.currency
            else None
        )
        data["store"] = (
            CatalogoSerializer(instance.store).data
            if instance.store
            else None
        )
        data["purchaseState"] = (
            CatalogoSerializer(instance.purchaseState).data
            if instance.purchaseState
            else None
        )
        return data
