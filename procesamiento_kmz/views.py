from django.shortcuts import render
from django.http import JsonResponse
from .models import Permiso, Area
from .forms import RegionPermitidaForm

def evaluar_region(request):
    if request.method == 'POST':
        form = RegionPermitidaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                print("form.extraer_geometria()")
                geometria = form.extraer_geometria()
                print("Compare Area's")
                areas = Area.objects.filter(region_permitida__contains=geometria).select_related('permiso')
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