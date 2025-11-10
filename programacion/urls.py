from django.urls import path
from .views import VehiculoListView, ConductorListView, ProgramacionDiariaView

urlpatterns = [
    path('vehiculos/', VehiculoListView.as_view(), name='vehiculos-list'),
    path('conductores/', ConductorListView.as_view(), name='conductores-list'),
    path('programacion-diaria/', ProgramacionDiariaView.as_view(), name='programacion-list'),
]
