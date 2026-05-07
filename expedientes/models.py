from django.db import models
from django.utils import timezone

from documents.models import Document, PurchaseOrder


class Expediente(models.Model):
    expedienteid = models.AutoField(primary_key=True)
    facturaid = models.ForeignKey(
        Document,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="facturaid",
        related_name="expedientes",
        null=True,
        blank=True,
    )
    ordencompraid = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="ordencompraid",
        related_name="expedientes",
        null=True,
        blank=True,
    )
    estado = models.BooleanField(default=True)
    lock_exp = models.BooleanField(default=False)
    createdby = models.IntegerField(null=True, blank=True)
    createat = models.DateTimeField(default=timezone.now)
    updatedby = models.IntegerField(null=True, blank=True)
    updatedat = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "expediente"

    def __str__(self):
        return f"Expediente {self.expedienteid}"


class ExpedienteDocumento(models.Model):
    expedientedocid = models.AutoField(primary_key=True)
    expedienteid = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        db_column="expedienteid",
        related_name="expediente_documentos",
    )
    tipodocumentoid = models.IntegerField(null=True, blank=True)
    filename = models.TextField(null=True, blank=True)
    filepath = models.TextField(null=True, blank=True)
    estado = models.BooleanField(default=True)
    createdby = models.IntegerField(null=True, blank=True)
    createat = models.DateTimeField(default=timezone.now)
    updatedby = models.IntegerField(null=True, blank=True)
    updatedat = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "expediente_documento"

    def __str__(self):
        return self.filename or f"Documento {self.expedientedocid}"
