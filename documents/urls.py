from django.urls import path
from .views import (
    DocumentDeleteView,
    DocumentDetailView,
    DocumentListCreateView,
    PurchaseOrderCreateView,
    PurchaseOrderDetailView,
    PurchaseOrderStatusUpdateView,
    TipoDocumentoView,
)

urlpatterns = [
    path("tipo-documento/", TipoDocumentoView.as_view(), name="tipo-documento"),
    path("documents/", DocumentListCreateView.as_view(), name="documents-list-create"),
    path("documents/<int:pk>/", DocumentDetailView.as_view(), name="documents-detail"),
    path("document-delete/", DocumentDeleteView.as_view(), name="document-delete"),
    path("purchase-orders/", PurchaseOrderCreateView.as_view(), name="purchase-order-create"),
    path("purchase-orders/<int:pk>/", PurchaseOrderDetailView.as_view(), name="purchase-order-detail"),
    path("purchase-orders/status/", PurchaseOrderStatusUpdateView.as_view(), name="purchase-order-status-update"),
]
