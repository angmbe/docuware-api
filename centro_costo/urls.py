from django.urls import path
from .views import CentroCostoListView

urlpatterns = [
    path("centro-costo/", CentroCostoListView.as_view(), name="centro-costo"),
]
