from django.contrib import admin

from .models import Concept, Destino, ExpenseRequest, ExpenseRequestDetail, Trip


admin.site.register(Concept)
admin.site.register(Destino)
admin.site.register(Trip)
admin.site.register(ExpenseRequest)
admin.site.register(ExpenseRequestDetail)
