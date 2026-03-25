from django.db import models
from django.utils import timezone

from catalogos.models import Catalogo


class Proveedor(models.Model):
    supplierid = models.AutoField(primary_key=True)
    supplierno = models.CharField(max_length=20, null=True, blank=True, unique=True)
    suppliername = models.CharField(max_length=500)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    bank1 = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="bank1",
        related_name="proveedores_bank1",
        null=True,
        blank=True,
    )
    accountno1 = models.CharField(max_length=50, null=True, blank=True)
    bank2 = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="bank2",
        related_name="proveedores_bank2",
        null=True,
        blank=True,
    )
    accountno2 = models.CharField(max_length=50, null=True, blank=True)
    createdby = models.IntegerField(null=True, blank=True)
    createdat = models.DateTimeField(default=timezone.now)
    updatedby = models.IntegerField(null=True, blank=True)
    updatedat = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "proveedor"

    def __str__(self):
        return self.suppliername
