from django.urls import path

from .views import CatalogoListView


urlpatterns = [
    path("catalogos/", CatalogoListView.as_view(), name="catalogos-list"),
]
