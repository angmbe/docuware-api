from django.urls import path

from .views import GetDocumentosSunatView


urlpatterns = [
    path(
        "apisunat/GetDocumentosSunat/",
        GetDocumentosSunatView.as_view(),
        name="get-documentos-sunat",
    ),
]
