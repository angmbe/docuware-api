from django.db import models
from django.utils import timezone

from programacion.models import Conductor, Vehiculo


class Concept(models.Model):
    id_concept = models.AutoField(primary_key=True)
    nombre_concepto = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "concept"

    def __str__(self):
        return self.nombre_concepto or f"Concepto {self.id_concept}"


class Destino(models.Model):
    idorigen = models.AutoField(primary_key=True)
    nombre_origen = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "destinos"

    def __str__(self):
        return self.nombre_origen or f"Destino {self.idorigen}"


class Trip(models.Model):
    id_trip = models.AutoField(primary_key=True)
    trip_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle = models.ForeignKey(
        Vehiculo,
        on_delete=models.DO_NOTHING,
        db_column="vehicle_id",
        db_constraint=False,
        related_name="trips",
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        Conductor,
        on_delete=models.DO_NOTHING,
        db_column="driver_id",
        db_constraint=False,
        related_name="trips",
        null=True,
        blank=True,
    )
    origin = models.ForeignKey(
        Destino,
        on_delete=models.DO_NOTHING,
        db_column="origin",
        db_constraint=False,
        related_name="origin_trips",
        null=True,
        blank=True,
    )
    destination = models.ForeignKey(
        Destino,
        on_delete=models.DO_NOTHING,
        db_column="destination",
        db_constraint=False,
        related_name="destination_trips",
        null=True,
        blank=True,
    )
    departure_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "trip"

    def __str__(self):
        return self.trip_number or f"Trip {self.id_trip}"


class ExpenseRequest(models.Model):
    id_request = models.AutoField(primary_key=True)
    id_trip = models.ForeignKey(
        Trip,
        on_delete=models.DO_NOTHING,
        db_column="id_trip",
        db_constraint=False,
        related_name="expense_requests",
        null=True,
        blank=True,
    )
    request_number = models.CharField(max_length=20, null=True, blank=True)
    requester_name = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "expenserequest"

    def __str__(self):
        return self.request_number or f"Solicitud {self.id_request}"


class ExpenseRequestDetail(models.Model):
    expense_detail_id = models.AutoField(primary_key=True)
    id_request = models.ForeignKey(
        ExpenseRequest,
        on_delete=models.CASCADE,
        db_column="id_request",
        db_constraint=False,
        related_name="details",
    )
    id_concept = models.ForeignKey(
        Concept,
        on_delete=models.DO_NOTHING,
        db_column="id_concept",
        db_constraint=False,
        related_name="expense_details",
        null=True,
        blank=True,
    )
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "expenserequestdetail"

    def __str__(self):
        return f"Detalle {self.expense_detail_id}"
