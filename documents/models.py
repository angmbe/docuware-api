from django.db import models

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

