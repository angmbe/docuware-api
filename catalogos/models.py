from django.db import models
from django.utils import timezone


class Catalogo(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_catalogo = models.CharField(max_length=50)
    codigo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=150)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "catalogo"

    def __str__(self):
        return f"{self.tipo_catalogo} - {self.codigo}"
