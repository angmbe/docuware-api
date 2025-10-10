from django.db import models

class DocumentDetail(models.Model):
    detailid = models.AutoField(primary_key=True)
    documentserial = models.CharField(max_length=50)
    documentnumber = models.CharField(max_length=50)
    suppliernumber = models.CharField(max_length=50)
    unit_measure_description = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField()
    unit_value = models.DecimalField(max_digits=12, decimal_places=2)
    tax_value = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.BooleanField(default=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    vehicle_no = models.CharField(max_length=10, null=True, blank=True) 

    class Meta:
        db_table = "documents_detail"
