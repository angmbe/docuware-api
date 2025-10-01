from django.urls import path
from .views import DocumentDetailView

urlpatterns = [
    path("documents-detail/", DocumentDetailView.as_view()),          # GET con filtros, POST
    path("documents-detail/<int:pk>/", DocumentDetailView.as_view()), # PUT
]