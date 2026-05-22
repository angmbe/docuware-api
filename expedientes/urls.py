from django.urls import path

from .views import (
    ExpedienteDetailView,
    ExpedienteDocumentoDetailView,
    ExpedienteDocumentoUploadView,
    ExpedienteListCreateView,
    ExpedienteUploadView,
    LockedExpedienteView,
)


urlpatterns = [
    path("expedientes/", ExpedienteListCreateView.as_view(), name="expedientes-list-create"),
    path("expedientes/<int:expedienteid>/", ExpedienteDetailView.as_view(), name="expedientes-detail"),
    path(
        "expedientes/<int:expedienteid>/documentos/",
        ExpedienteDocumentoUploadView.as_view(),
        name="expedientes-documentos-upload",
    ),
    path(
        "expedientes/documentos/<int:expedientedocid>/",
        ExpedienteDocumentoDetailView.as_view(),
        name="expedientes-documentos-detail",
    ),
    path("locked_expediente/", LockedExpedienteView.as_view(), name="locked-expediente"),
    path("expedientes/upload/", ExpedienteUploadView.as_view(), name="expedientes-upload"),
]
