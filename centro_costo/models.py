from django.db import models

class CentroCosto(models.Model):
    centroid = models.AutoField(primary_key=True)
    centrocodigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)

    class Meta:
        db_table = 'centro_costo'

    def __str__(self):
        return f"{self.centrocodigo} - {self.descripcion}"
