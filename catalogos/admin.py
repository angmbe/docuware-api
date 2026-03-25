from django.contrib import admin

from .models import Catalogo


@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo_catalogo", "codigo", "descripcion", "estado")
    list_filter = ("tipo_catalogo", "estado")
    search_fields = ("tipo_catalogo", "codigo", "descripcion")
