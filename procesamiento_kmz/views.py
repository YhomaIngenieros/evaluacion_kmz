from django.shortcuts import render
from django.http import JsonResponse

from .models import Permiso, Area
from .forms import RegionPermitidaForm

import json

def evaluar_region(request):
    if request.method != "POST":
        form = RegionPermitidaForm()
        return render(request, "evaluar_region.html", {"form": form})

    form = RegionPermitidaForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse(
            {"valido": False, "mensaje": form.errors.get_json_data()},
            status=400,
        )

    try:
        geometria = form.extraer_geometria()

        # Una sola Area no necesita contener el polígono completo:
        # se consideran todas las áreas que lo intersectan.
        areas = list(
            Area.objects.filter(
                estado=True,
                region_permitida__intersects=geometria,
            ).select_related("permiso")
        )

        if not areas:
            return JsonResponse({
                "valido": False,
                "mensaje": "El polígono no intersecta ninguna área permitida.",
                "regiones_faltantes": json.loads(geometria.geojson),
            })

        cobertura = areas[0].region_permitida
        for area in areas[1:]:
            cobertura = cobertura.union(area.region_permitida)

        faltante = geometria.difference(cobertura)
        nombres_areas = [area.nombre for area in areas]

        if faltante.empty:
            return JsonResponse({
                "valido": True,
                "mensaje": "El polígono está completamente cubierto.",
                "areas": nombres_areas,
            })

        return JsonResponse({
            "valido": False,
            "mensaje": "El polígono está cubierto parcialmente.",
            "areas_intersectadas": nombres_areas,
            "regiones_faltantes": json.loads(faltante.geojson),
        })

    except Exception as exc:
        return JsonResponse(
            {"valido": False, "mensaje": str(exc)},
            status=400,
        )
    
def evaluar_region2(request):
    if request.method == 'POST':
        form = RegionPermitidaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                geometria = form.extraer_geometria()
                areas = Area.objects.filter(estado=True,region_permitida__contains=geometria).select_related('permiso')
                print("areas")
                print(areas)
                if areas.exists():
                    return JsonResponse({
                        'valido': True,
                        'mensaje': 'La región proporcionada es válida.',
                        'permisos': list(areas.values_list('permiso__nombre', flat=True).distinct()),
                    })
                else:
                    return JsonResponse({
                        'valido': False,
                        'mensaje': 'La región proporcionada no coincide con ninguna región permitida.'
                    })
            except Exception as e:
                return JsonResponse({'valido': False, 'mensaje': str(e)})
    else:
        form = RegionPermitidaForm()

    return render(request, 'evaluar_region.html', {'form': form})