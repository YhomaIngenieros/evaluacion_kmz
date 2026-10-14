from django.urls import path
from .views import evaluar_region

urlpatterns = [
    path('evaluar-region/', evaluar_region, name='evaluar_region'),
]