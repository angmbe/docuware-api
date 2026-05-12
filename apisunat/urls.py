from django.urls import path

from .views import GetDocumentosSunatJobView, GetDocumentosSunatView


urlpatterns = [
    path(
        "apisunat/GetDocumentosSunat/",
        GetDocumentosSunatView.as_view(),
        name="get-documentos-sunat",
    ),
    path(
        "apisunat/GetDocumentosSunat/jobs/<str:job_id>/",
        GetDocumentosSunatJobView.as_view(),
        name="get-documentos-sunat-job",
    ),
]
