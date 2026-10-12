from datetime import datetime
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.utils import timezone
from .models import Visita

class AccionSalidaForm(ActionForm):
    hora_salida_masiva = forms.DateTimeField(
        label="Hora de salida para selección (manual)",
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rut", "motivo", "hora_entrada", "hora_salida", "estado")
    list_filter = ("hora_entrada", ("hora_salida", admin.EmptyFieldListFilter))
    search_fields = ("nombre", "rut", "motivo")
    readonly_fields = ()
    list_per_page = 20
    actions = ("registrar_salida_masiva",)
    action_form = AccionSalidaForm

    @admin.display(description="Estado")
    def estado(self, obj):
        return "Finalizada" if obj.hora_salida else "Dentro"

    @admin.action(description="Marcar salida de visitas seleccionadas (hora manual)")
    def registrar_salida_masiva(self, request, queryset):
        bruto = request.POST.get("hora_salida_masiva", "").strip()
        if not bruto:
            self.message_user(request, "Ingresa primero la fecha y hora manual de salida en la barra de acciones.", level=messages.ERROR)
            return
        try:
            fecha = datetime.fromisoformat(bruto)
            if timezone.is_naive(fecha):
                fecha = timezone.make_aware(fecha, timezone.get_current_timezone())
        except (ValueError, OverflowError):
            self.message_user(request, "La fecha y hora de salida no son válidas.", level=messages.ERROR)
            return
        pendientes = queryset.filter(hora_salida__isnull=True, hora_entrada__lte=fecha)
        cantidad = pendientes.update(hora_salida=fecha)
        omitidas = queryset.count() - cantidad
        if cantidad:
            self.message_user(request, f"Se registró la salida de {cantidad} visita(s).", level=messages.SUCCESS)
        if omitidas:
            self.message_user(request, f"Se omitieron {omitidas} visita(s) ya cerradas o con entrada posterior a la salida.", level=messages.WARNING)

admin.site.site_header = "Administración de Registro de Visitas"
admin.site.site_title = "Control de Visitas"
admin.site.index_title = "Gestión de visitas"
