from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from catalogos.serializers import CatalogoSerializer
from documents.serializers import TipoDocumentoSerializer
from programacion.serializers import VehiculoSerializer
from users.serializers import UserSerializer

from .models import (
    Concept,
    Destino,
    ExpenseRequest,
    ExpenseRequestDetail,
    ExpenseVoucher,
    Trip,
)


class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = "__all__"
        read_only_fields = ("id_concept",)


class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = "__all__"
        read_only_fields = ("idorigen",)


class TripSerializer(serializers.ModelSerializer):
    vehicle = VehiculoSerializer(read_only=True)
    driver = UserSerializer(read_only=True)
    origin_data = DestinoSerializer(source="origin", read_only=True)
    destination_data = DestinoSerializer(source="destination", read_only=True)

    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip._meta.get_field("vehicle").remote_field.model.objects.all(),
        source="vehicle",
        required=False,
        allow_null=True,
    )
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Trip._meta.get_field("driver").remote_field.model.objects.all(),
        source="driver",
        required=False,
        allow_null=True,
    )
    origin = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.all(),
        required=False,
        allow_null=True,
    )
    destination = serializers.PrimaryKeyRelatedField(
        queryset=Destino.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Trip
        fields = [
            "id_trip",
            "trip_number",
            "vehicle_id",
            "vehicle",
            "driver_id",
            "driver",
            "origin",
            "origin_data",
            "destination",
            "destination_data",
            "departure_date",
            "return_date",
            "notes",
            "status",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ("id_trip", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data.setdefault("created_at", timezone.now())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = timezone.now()
        return super().update(instance, validated_data)


class ExpenseRequestDetailSerializer(serializers.ModelSerializer):
    expense_detail_id = serializers.IntegerField(required=False)
    id_request = serializers.PrimaryKeyRelatedField(
        queryset=ExpenseRequest.objects.all(),
        required=False,
    )
    concept = ConceptSerializer(source="id_concept", read_only=True)

    class Meta:
        model = ExpenseRequestDetail
        fields = [
            "expense_detail_id",
            "id_request",
            "id_concept",
            "concept",
            "budgeted_amount",
            "notes",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ("created_at", "updated_at")
        extra_kwargs = {
            "expense_detail_id": {"required": False},
        }


class ExpenseRequestTripSequenceSerializer(serializers.ModelSerializer):
    details = ExpenseRequestDetailSerializer(many=True, read_only=True)
    status_data = CatalogoSerializer(source="status", read_only=True)

    class Meta:
        model = ExpenseRequest
        fields = [
            "id_request",
            "request_number",
            "requester_name",
            "reason",
            "total_budget",
            "status",
            "status_data",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "details",
        ]


class TripSequenceSerializer(TripSerializer):
    expense_requests = ExpenseRequestTripSequenceSerializer(many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ["expense_requests"]


class ExpenseRequestSerializer(serializers.ModelSerializer):
    details = ExpenseRequestDetailSerializer(many=True, required=False)
    trip = TripSerializer(source="id_trip", read_only=True)
    status_data = CatalogoSerializer(source="status", read_only=True)

    class Meta:
        model = ExpenseRequest
        fields = [
            "id_request",
            "id_trip",
            "trip",
            "request_number",
            "requester_name",
            "reason",
            "total_budget",
            "status",
            "status_data",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "details",
        ]
        read_only_fields = ("id_request", "created_at", "updated_at")

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])
        now = timezone.now()
        validated_data.setdefault("created_at", now)

        with transaction.atomic():
            expense_request = ExpenseRequest.objects.create(**validated_data)
            self._upsert_details(expense_request, details_data, now)

        return self._reload(expense_request.pk)

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        now = timezone.now()

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.updated_at = now
            instance.save()

            if details_data is not None:
                self._upsert_details(instance, details_data, now)

        return self._reload(instance.pk)

    def _upsert_details(self, expense_request, details_data, now):
        for detail_data in details_data:
            detail_id = detail_data.pop("expense_detail_id", None)
            detail_data.pop("id_request", None)

            if detail_id:
                try:
                    detail = ExpenseRequestDetail.objects.get(
                        expense_detail_id=detail_id,
                        id_request=expense_request,
                    )
                except ExpenseRequestDetail.DoesNotExist as exc:
                    raise serializers.ValidationError(
                        {
                            "details": [
                                f"El detalle {detail_id} no pertenece a la solicitud."
                            ]
                        }
                    ) from exc
                for attr, value in detail_data.items():
                    setattr(detail, attr, value)
                detail.updated_at = now
                detail.save()
            else:
                detail_data.setdefault("created_at", now)
                ExpenseRequestDetail.objects.create(
                    id_request=expense_request,
                    **detail_data,
                )

    def _reload(self, pk):
        return (
            ExpenseRequest.objects.select_related("id_trip", "status")
            .prefetch_related("details", "details__id_concept")
            .get(pk=pk)
        )


class ExpenseVoucherSerializer(serializers.ModelSerializer):
    expense_voucher_id = serializers.IntegerField(required=False)
    document_type_data = TipoDocumentoSerializer(source="document_type", read_only=True)
    status_data = CatalogoSerializer(source="status", read_only=True)

    class Meta:
        model = ExpenseVoucher
        fields = [
            "expense_voucher_id",
            "id_request",
            "expense_detail_id",
            "document_type",
            "document_type_data",
            "supplier_ruc",
            "series_number",
            "voucher_number",
            "amount",
            "photo_url",
            "rejection_reason",
            "status",
            "status_data",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        request_instance = attrs.get("id_request") or getattr(
            self.instance,
            "id_request",
            None,
        )
        detail_instance = attrs.get("expense_detail_id") or getattr(
            self.instance,
            "expense_detail_id",
            None,
        )

        if request_instance and detail_instance:
            detail_request_id = getattr(detail_instance, "id_request_id", None)
            if detail_request_id != request_instance.pk:
                raise serializers.ValidationError(
                    {
                        "expense_detail_id": [
                            "El detalle no pertenece a la solicitud indicada."
                        ]
                    }
                )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault("created_at", timezone.now())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_at"] = timezone.now()
        return super().update(instance, validated_data)
