from django.shortcuts import render
from django.http import JsonResponse
from .models import Permiso
from .forms import RegionPermitidaForm

def evaluar_region(request):
    if request.method == 'POST':
        form = RegionPermitidaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                geometria = form.extraer_geometria()
                permisos = Permiso.objects.filter(region_permitida__contains=geometria)
                if permisos.exists():
                    return JsonResponse({
                        'valido': True,
                        'mensaje': 'La región proporcionada es válida.',
                        'permisos': [permiso.nombre for permiso in permisos]
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