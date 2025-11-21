from django.db import models

class DimPeriodo(models.Model):
    PeriodoKey = models.IntegerField(primary_key=True)
    Periodo = models.CharField(max_length=8)
    Fecha = models.DateField()
    Anio = models.IntegerField()
    Semestre = models.CharField(max_length=30)
    Trimestre = models.CharField(max_length=30)
    Mes = models.CharField(max_length=20)
    Dia = models.IntegerField()
    NroMes = models.IntegerField()

    class Meta:
        db_table = 'DimPeriodo'

    def __str__(self):
        return self.Periodo
        
class MAESTRO_HIS_ESTABLECIMIENTO(models.Model):
    Id_Establecimiento = models.IntegerField(primary_key=True)
    Nombre_Establecimiento = models.CharField(max_length=100)
    Ubigueo_Establecimiento = models.CharField(max_length=6)
    Codigo_Disa = models.IntegerField()
    Disa = models.CharField(max_length=80)
    Codigo_Red = models.CharField(max_length=2)
    Red = models.CharField(max_length=70)
    Codigo_MicroRed = models.CharField(max_length=2)
    MicroRed = models.CharField(max_length=70)
    Codigo_Unico = models.CharField(max_length=9)
    Codigo_Sector = models.IntegerField()
    Descripcion_Sector = models.CharField(max_length=50)
    Departamento = models.CharField(max_length=150)
    Provincia = models.CharField(max_length=150)
    Distrito = models.CharField(max_length=150)
    Categoria_Establecimiento = models.CharField(max_length=10)

    class Meta:
        db_table = 'MAESTRO_HIS_ESTABLECIMIENTO'
        managed = False  # Indica que Django no debe gestionar esta tabla

    def __str__(self):
        return self.Nombre_Establecimiento

class DimDiscapacidadEtapa(models.Model):
    EtapaKey = models.IntegerField(primary_key=True)
    Etapa = models.CharField(max_length=20)

    class Meta:
        db_table = 'DimDiscapacidadEtapa'

    def __str__(self):
        return self.Etapa

class Actualizacion(models.Model):
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    Descripcion = models.CharField(max_length=100,null=True, blank=True)
    
    def __str__(self):
        return self.Descripcion




