from django.urls import path

from .views import (
    ExpedienteDetailView,
    ExpedienteDocumentoUploadView,
    ExpedienteListCreateView,
    ExpedienteUploadView,
)


urlpatterns = [
    path("expedientes/", ExpedienteListCreateView.as_view(), name="expedientes-list-create"),
    path("expedientes/<int:expedienteid>/", ExpedienteDetailView.as_view(), name="expedientes-detail"),
    path(
        "expedientes/<int:expedienteid>/documentos/",
        ExpedienteDocumentoUploadView.as_view(),
        name="expedientes-documentos-upload",
    ),
    path("expedientes/upload/", ExpedienteUploadView.as_view(), name="expedientes-upload"),
]
