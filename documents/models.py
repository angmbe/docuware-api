from django.db import models

from catalogos.models import Catalogo
from proveedores.models import Proveedor

class TipoDocumento(models.Model):
    tipoid = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tipo
    
    class Meta:
        db_table = "tipo_documento"
    
class Document(models.Model):
    documentid = models.AutoField(primary_key=True)
    customer = models.CharField(max_length=50, null=True, blank=True)
    documentserial = models.CharField(max_length=50, null=True, blank=True)
    documentnumber = models.CharField(max_length=50, null=True, blank=True)
    suppliernumber = models.CharField(max_length=50, null=True, blank=True)
    suppliername = models.CharField(max_length=100, null=True, blank=True)
    #documenttype = models.IntegerField()
    documenttype = models.ForeignKey(
        TipoDocumento,
        on_delete=models.DO_NOTHING,   # no cascada, no bloquea
        db_constraint=False,           # 🚨 evita que Django cree la FK en DB
        db_column="documenttype",      # mantiene el nombre original
        null=True,
        blank=True
    )
    documentdate = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    taxamount = models.DecimalField(max_digits=12, decimal_places=2)
    totalamount = models.DecimalField(max_digits=12, decimal_places=2)
    documenturl = models.CharField(max_length=1000, null=True, blank=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    driver = models.CharField(max_length=100, null=True, blank=True)
    #centercost = models.CharField(max_length=100, null=True, blank=True)
    centercost = models.ForeignKey(
    'centro_costo.CentroCosto',
    on_delete=models.DO_NOTHING,
    db_constraint=False,
    db_column="centercost",
    related_name="documents",
    null=True,
    blank=True
    )
    status = models.BooleanField(default=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    class Meta:
        db_table = "documents"

class PurchaseOrder(models.Model):
    purchaseOrderID = models.AutoField(primary_key=True, db_column="purchaseorderid")
    orderNo = models.CharField(max_length=20, null=True, blank=True, db_column="orderno")
    supplierID = models.ForeignKey(
        Proveedor,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="supplierid",
        related_name="purchase_orders",
        null=True,
        blank=True,
    )
    documentAssociatedType = models.ForeignKey(
        TipoDocumento,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="documentassociatedtype",
        related_name="purchase_orders",
        null=True,
        blank=True,
    )
    documentAssociatedNo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="documentassociatedno",
    )
    paymentCondition = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="paymentcondition",
        related_name="purchase_orders_payment_condition",
        null=True,
        blank=True,
    )
    currency = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="currency",
        related_name="purchase_orders_currency",
        null=True,
        blank=True,
    )
    guideNo = models.CharField(max_length=20, null=True, blank=True, db_column="guideno")
    store = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="store",
        related_name="purchase_orders_store",
        null=True,
        blank=True,
    )
    purchaseState = models.ForeignKey(
        Catalogo,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        db_column="purchasestate",
        related_name="purchase_orders_state",
        null=True,
        blank=True,
    )
    createdBy = models.IntegerField(null=True, blank=True, db_column="createdby")
    createAt = models.DateField(null=True, blank=True, db_column="createat")
    updatedBy = models.IntegerField(null=True, blank=True, db_column="updatedby")
    updatedAt = models.DateField(null=True, blank=True, db_column="updatedat")

    class Meta:
        db_table = "purchaseorder"

    def __str__(self):
        return self.orderNo or f"PO-{self.purchaseOrderID}"


class PurchaseOrderDetail(models.Model):
    purchaseDetailID = models.AutoField(primary_key=True, db_column="purchasedetailid")
    purchaseOrderID = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        db_column="purchaseorderid",
        related_name="details",
    )
    descriptionItem = models.TextField(null=True, blank=True, db_column="descriptionitem")
    quantity = models.IntegerField(null=True, blank=True, db_column="quantity")
    unitPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="unitprice",
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="total",
    )
    createdBy = models.IntegerField(null=True, blank=True, db_column="createdby")
    createAt = models.DateField(null=True, blank=True, db_column="createat")
    updatedBy = models.IntegerField(null=True, blank=True, db_column="updatedby")
    updatedAt = models.DateField(null=True, blank=True, db_column="updatedat")

    class Meta:
        db_table = "purchaseorderdetail"

    def __str__(self):
        return f"{self.purchaseDetailID} - {self.descriptionItem or 'Sin descripcion'}"
