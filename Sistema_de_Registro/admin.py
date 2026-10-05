from django.contrib import admin
from .models import Visita

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "rut",
        "motivo",
        "hora_entrada",
        "hora_salida",
    )

    search_fields = (
        "nombre",
        "rut",
        "motivo",
    )

    list_filter = (
        "hora_entrada",
    )