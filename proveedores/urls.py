from django.urls import path

from .views import ProveedorListCreateView


urlpatterns = [
    path("proveedores/", ProveedorListCreateView.as_view(), name="proveedores-list-create"),
]
