from django.urls import path
from .views import DocumentDetailView, DocumentFullView

urlpatterns = [
    path("documents-detail/", DocumentDetailView.as_view()),          # GET con filtros, POST
    path("documents-all", DocumentFullView.as_view(), name='documents-all'),  # GET match document y detail
    path("documents-detail/<int:pk>/", DocumentDetailView.as_view()), # PUT
]