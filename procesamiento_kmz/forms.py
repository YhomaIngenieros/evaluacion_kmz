from io import BytesIO
from zipfile import BadZipFile, ZipFile

from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from fastkml import kml

from .models import Area, Permiso


class RegionPermitidaForm(forms.Form):
    archivo = forms.FileField()

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        if not archivo.name.lower().endswith((".kmz", ".kml")):
            raise ValidationError("El archivo debe ser de tipo KMZ o KML.")
        return archivo

    def extraer_geometria(self):
        archivo = self.cleaned_data["archivo"]
        contenido = archivo.read()
        nombre = archivo.name.lower()

        if nombre.endswith(".kml"):
            print("archivo kml")
            geometria = self._geometria_desde_kml(contenido)
            if geometria is not None:
                return geometria

        elif nombre.endswith(".kmz"):
            print("archivo kml")

            try:
                with ZipFile(BytesIO(contenido)) as kmz:
                    archivos_kml = [
                        nombre_kml
                        for nombre_kml in kmz.namelist()
                        if nombre_kml.lower().endswith(".kml")
                    ]

                    for nombre_kml in archivos_kml:
                        geometria = self._geometria_desde_kml(
                            kmz.read(nombre_kml)
                        )
                        if geometria is not None:
                            return geometria

            except BadZipFile as exc:
                raise ValidationError("El archivo KMZ no es un ZIP válido.") from exc

        raise ValidationError(
            "No se encontró ninguna geometría en el archivo."
        )

    def _geometria_desde_kml(self, contenido):
        try:
            texto_kml = contenido.decode("utf-8-sig")
            kml_obj = kml.KML.from_string(texto_kml)
        except Exception as exc:
            raise ValidationError(
                f"No se pudo procesar el archivo KML: {exc}"
            ) from exc

        for feature in self._recorrer_features(kml_obj.features):
            geometria_kml = getattr(feature, "geometry", None)
            if geometria_kml is None:
                continue

            try:
                return GEOSGeometry(geometria_kml.wkt, srid=4326)
            except Exception as exc:
                raise ValidationError(
                    f"No se pudo convertir la geometría: {exc}"
                ) from exc

        return None

    @classmethod
    def _recorrer_features(cls, features):
        for feature in features:
            yield feature

            features_anidadas = getattr(feature, "features", None)
            if features_anidadas:
                yield from cls._recorrer_features(features_anidadas)


class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ["nombre", "descripcion"]


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ["nombre", "region_permitida", "permiso"]