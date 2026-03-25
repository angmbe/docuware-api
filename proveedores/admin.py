from django.contrib import admin

from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("supplierid", "supplierno", "suppliername", "phone", "email")
    search_fields = ("supplierno", "suppliername", "email")
