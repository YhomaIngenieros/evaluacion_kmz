from django.contrib.gis.db import models

class Permiso(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
class Area(models.Model):
    nombre = models.CharField(max_length=255)
    permiso = models.ForeignKey(Permiso, related_name='areas_permiso', on_delete=models.DO_NOTHING)
    region_permitida = models.PolygonField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

