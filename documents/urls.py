from django.urls import path
from .views import DocumentListCreateView, DocumentDetailView, TipoDocumentoView,DocumentDeleteView

urlpatterns = [
    path("tipo-documento/", TipoDocumentoView.as_view(), name="tipo-documento"),
    path("documents/", DocumentListCreateView.as_view(), name="documents-list-create"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="documents-detail"),
    path("document-delete/", DocumentDeleteView.as_view(), name="document-delete"),
]
