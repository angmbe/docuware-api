from django.db import models

class Vehiculo(models.Model):
    idvehiculo = models.BigAutoField(primary_key=True)
    no_vehiculo = models.CharField(max_length=50)

    class Meta:
        db_table = "vehiculos"

    def __str__(self):
        return self.no_vehiculo


class Conductor(models.Model):
    idconductor = models.BigAutoField(primary_key=True)
    conductor_nm = models.CharField(max_length=100)

    class Meta:
        db_table = "conductores"

    def __str__(self):
        return self.conductor_nm


class ProgramacionDiaria(models.Model):
    programacionid = models.BigAutoField(primary_key=True)
    programacionfecha = models.DateField()
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.DO_NOTHING, db_column="idvehiculo", db_constraint=False)
    conductor = models.ForeignKey(Conductor, on_delete=models.DO_NOTHING, db_column="idconductor", db_constraint=False)

    class Meta:
        db_table = "programacion_diaria"
