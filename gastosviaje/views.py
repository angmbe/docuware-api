from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from utils.responses import standard_response

from .models import (
    Concept,
    Destino,
    ExpenseRequest,
    ExpenseRequestDetail,
    ExpenseVoucher,
    Trip,
)
from .serializers import (
    ConceptSerializer,
    DestinoSerializer,
    ExpenseRequestDetailSerializer,
    ExpenseRequestSerializer,
    ExpenseVoucherSerializer,
    TripSequenceSerializer,
    TripSerializer,
)


class BaseListPostView(APIView):
    model = None
    serializer_class = None
    pk_field = "id"
    order_by = None
    list_message = "Registros obtenidos correctamente"
    detail_message = "Registro obtenido correctamente"
    create_message = "Registro creado correctamente"
    update_message = "Registro actualizado correctamente"
    error_message = "Error al procesar el registro"
    not_found_message = "Registro no encontrado"
    select_related_fields = ()
    prefetch_related_fields = ()

    def get_queryset(self):
        queryset = self.model.objects.all()
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        return queryset

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request, pk=None):
        query_pk = pk or request.query_params.get(self.pk_field)
        queryset = self.get_queryset()
        serializer_class = self.get_serializer_class()

        if query_pk:
            try:
                instance = queryset.get(**{self.pk_field: query_pk})
            except self.model.DoesNotExist:
                return standard_response(
                    success=False,
                    message=self.not_found_message,
                    data=None,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            serializer = serializer_class(instance)
            return standard_response(
                success=True,
                message=self.detail_message,
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        if self.order_by:
            queryset = queryset.order_by(self.order_by)

        serializer = serializer_class(queryset, many=True)
        return standard_response(
            success=True,
            message=self.list_message,
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def post(self, request):
        instance = None
        instance_id = request.data.get(self.pk_field)

        if instance_id:
            try:
                instance = self.get_queryset().get(**{self.pk_field: instance_id})
            except self.model.DoesNotExist:
                return standard_response(
                    success=False,
                    message=self.not_found_message,
                    data=None,
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=bool(instance),
        )
        if serializer.is_valid():
            try:
                saved_instance = serializer.save()
            except ValidationError as exc:
                return standard_response(
                    success=False,
                    message=self.error_message,
                    data=exc.detail,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            response_status = status.HTTP_200_OK if instance else status.HTTP_201_CREATED
            return standard_response(
                success=True,
                message=self.update_message if instance else self.create_message,
                data=self.serializer_class(saved_instance).data,
                status_code=response_status,
            )

        return standard_response(
            success=False,
            message=self.error_message,
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ConceptListPostView(BaseListPostView):
    model = Concept
    serializer_class = ConceptSerializer
    pk_field = "id_concept"
    order_by = "nombre_concepto"
    list_message = "Conceptos obtenidos correctamente"
    detail_message = "Concepto obtenido correctamente"
    create_message = "Concepto creado correctamente"
    update_message = "Concepto actualizado correctamente"
    error_message = "Error al procesar el concepto"
    not_found_message = "Concepto no encontrado"


class DestinoListPostView(BaseListPostView):
    model = Destino
    serializer_class = DestinoSerializer
    pk_field = "idorigen"
    order_by = "nombre_origen"
    list_message = "Destinos obtenidos correctamente"
    detail_message = "Destino obtenido correctamente"
    create_message = "Destino creado correctamente"
    update_message = "Destino actualizado correctamente"
    error_message = "Error al procesar el destino"
    not_found_message = "Destino no encontrado"


class TripListPostView(BaseListPostView):
    model = Trip
    serializer_class = TripSerializer
    pk_field = "id_trip"
    order_by = "-id_trip"
    select_related_fields = ("vehicle", "driver", "origin", "destination")
    list_message = "Viajes obtenidos correctamente"
    detail_message = "Viaje obtenido correctamente"
    create_message = "Viaje creado correctamente"
    update_message = "Viaje actualizado correctamente"
    error_message = "Error al procesar el viaje"
    not_found_message = "Viaje no encontrado"

    def get(self, request, pk=None):
        driver_id = request.query_params.get("driver_id")
        if driver_id and not driver_id.isdigit():
            return standard_response(
                success=False,
                message=self.error_message,
                data={"driver_id": ["Debe ser un numero entero."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return super().get(request, pk)

    def get_queryset(self):
        queryset = super().get_queryset()
        driver_id = self.request.query_params.get("driver_id")

        if driver_id:
            queryset = queryset.filter(driver_id=driver_id).prefetch_related(
                "expense_requests",
                "expense_requests__details",
                "expense_requests__details__id_concept",
            )

        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET" and self.request.query_params.get("driver_id"):
            return TripSequenceSerializer
        return super().get_serializer_class()


class ExpenseRequestListPostView(BaseListPostView):
    model = ExpenseRequest
    serializer_class = ExpenseRequestSerializer
    pk_field = "id_request"
    order_by = "-id_request"
    select_related_fields = ("id_trip",)
    prefetch_related_fields = ("details", "details__id_concept")
    list_message = "Solicitudes de gasto obtenidas correctamente"
    detail_message = "Solicitud de gasto obtenida correctamente"
    create_message = "Solicitud de gasto creada correctamente"
    update_message = "Solicitud de gasto actualizada correctamente"
    error_message = "Error al procesar la solicitud de gasto"
    not_found_message = "Solicitud de gasto no encontrada"


class ExpenseRequestDetailListPostView(BaseListPostView):
    model = ExpenseRequestDetail
    serializer_class = ExpenseRequestDetailSerializer
    pk_field = "expense_detail_id"
    order_by = "-expense_detail_id"
    select_related_fields = ("id_request", "id_concept")
    list_message = "Detalles de solicitud de gasto obtenidos correctamente"
    detail_message = "Detalle de solicitud de gasto obtenido correctamente"
    create_message = "Detalle de solicitud de gasto creado correctamente"
    update_message = "Detalle de solicitud de gasto actualizado correctamente"
    error_message = "Error al procesar el detalle de solicitud de gasto"
    not_found_message = "Detalle de solicitud de gasto no encontrado"

    def post(self, request):
        if not request.data.get("expense_detail_id") and not request.data.get("id_request"):
            return standard_response(
                success=False,
                message=self.error_message,
                data={"id_request": ["Este campo es obligatorio."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return super().post(request)


class ExpenseVoucherListPostView(BaseListPostView):
    model = ExpenseVoucher
    serializer_class = ExpenseVoucherSerializer
    pk_field = "expense_voucher_id"
    order_by = "-expense_voucher_id"
    select_related_fields = (
        "id_request",
        "expense_detail_id",
        "document_type",
        "status",
    )
    list_message = "Comprobantes de gasto obtenidos correctamente"
    detail_message = "Comprobante de gasto obtenido correctamente"
    create_message = "Comprobante de gasto creado correctamente"
    update_message = "Comprobante de gasto actualizado correctamente"
    error_message = "Error al procesar el comprobante de gasto"
    not_found_message = "Comprobante de gasto no encontrado"

    def get_queryset(self):
        queryset = super().get_queryset()
        id_request = self.request.query_params.get("id_request")
        expense_detail_id = self.request.query_params.get("expense_detail_id")

        if id_request:
            queryset = queryset.filter(id_request_id=id_request)
        if expense_detail_id:
            queryset = queryset.filter(expense_detail_id_id=expense_detail_id)

        return queryset
