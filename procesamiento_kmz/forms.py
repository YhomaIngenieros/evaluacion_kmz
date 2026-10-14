from .models import Permiso, Area
from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from fastkml import kml

class RegionPermitidaForm(forms.Form):
    archivo = forms.FileField()

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        if not archivo.name.endswith(('.kmz', '.kml')):
            raise ValidationError("El archivo debe ser de tipo KMZ o KML.")
        return archivo

    def extraer_geometria(self):
        archivo = self.cleaned_data['archivo']
        contenido = archivo.read()

        # Procesar KML
        if archivo.name.endswith('.kml'):
            kml_obj = kml.KML()
            kml_obj.from_string(contenido.decode('utf-8'))
            print("kml_obj")
            for document in kml_obj.features():  # Iterar sobre los documentos
                for feature in document.features():  # Iterar sobre las características
                    if hasattr(feature, 'geometry'):
                        return GEOSGeometry(feature.geometry.wkt)

        # Procesar KMZ
        elif archivo.name.endswith('.kmz'):
            import zipfile
            with zipfile.ZipFile(archivo, 'r') as z:
                for filename in z.namelist():
                    if filename.endswith('.kml'):
                        with z.open(filename) as kml_file:
                            kml_obj = kml.KML()
                            kml_obj.from_string(kml_file.read().decode('utf-8'))
                            for document in kml_obj.features():
                                for feature in document.features():
                                    if hasattr(feature, 'geometry'):
                                        return GEOSGeometry(feature.geometry.wkt)

        raise ValidationError("No se pudo extraer la geometría del archivo.")

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ['nombre', 'descripcion']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'region_permitida', 'permiso']


