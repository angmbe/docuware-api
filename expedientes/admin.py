from django.contrib import admin

from .models import Expediente, ExpedienteDocumento


class ExpedienteDocumentoInline(admin.TabularInline):
    model = ExpedienteDocumento
    extra = 0


@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ("expedienteid", "facturaid", "ordencompraid", "estado", "createdby")
    inlines = [ExpedienteDocumentoInline]
