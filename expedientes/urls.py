from django.urls import path

from .views import ExpedienteUploadView


urlpatterns = [
    path("expedientes/upload/", ExpedienteUploadView.as_view(), name="expedientes-upload"),
]
