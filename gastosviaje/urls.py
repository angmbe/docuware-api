from django.urls import path

from .views import (
    ConceptListPostView,
    DestinoListPostView,
    ExpenseRequestDetailListPostView,
    ExpenseRequestListPostView,
    ExpenseRequestStatusUpdateView,
    ExpenseVoucherListPostView,
    ExpenseVoucherPhotoUploadView,
    TripListPostView,
)


urlpatterns = [
    path("concepts/", ConceptListPostView.as_view(), name="concepts-list-post"),
    path("concepts/<int:pk>/", ConceptListPostView.as_view(), name="concepts-detail"),
    path("destinos/", DestinoListPostView.as_view(), name="destinos-list-post"),
    path("destinos/<int:pk>/", DestinoListPostView.as_view(), name="destinos-detail"),
    path("trips/", TripListPostView.as_view(), name="trips-list-post"),
    path("trips/<int:pk>/", TripListPostView.as_view(), name="trips-detail"),
    path(
        "expense-requests/",
        ExpenseRequestListPostView.as_view(),
        name="expense-requests-list-post",
    ),
    path(
        "expense-requests/<int:pk>/",
        ExpenseRequestListPostView.as_view(),
        name="expense-requests-detail",
    ),
    path(
        "expense-requests/status/",
        ExpenseRequestStatusUpdateView.as_view(),
        name="expense-requests-status-update",
    ),
    path(
        "expense-request-details/",
        ExpenseRequestDetailListPostView.as_view(),
        name="expense-request-details-list-post",
    ),
    path(
        "expense-request-details/<int:pk>/",
        ExpenseRequestDetailListPostView.as_view(),
        name="expense-request-details-detail",
    ),
    path(
        "expense-vouchers/",
        ExpenseVoucherListPostView.as_view(),
        name="expense-vouchers-list-post",
    ),
    path(
        "expense-vouchers/<int:pk>/",
        ExpenseVoucherListPostView.as_view(),
        name="expense-vouchers-detail",
    ),
    path(
        "expense-vouchers/<int:pk>/photo/",
        ExpenseVoucherPhotoUploadView.as_view(),
        name="expense-vouchers-photo-upload",
    ),
]
