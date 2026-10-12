import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Visita
from .rut import normalizar_rut

class FechaHoraWidget(forms.DateTimeInput):
    input_type = "datetime-local"
    def __init__(self, attrs=None):
        config = {"step": "60"}
        if attrs:
            config.update(attrs)
        super().__init__(attrs=config, format="%Y-%m-%dT%H:%M")

class VisitaForm(forms.ModelForm):
    hora_entrada = forms.DateTimeField(
        label="Fecha y hora de entrada (manual)",
        widget=FechaHoraWidget,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )

    class Meta:
        model = Visita
        fields = ("nombre", "rut", "motivo", "hora_entrada")
        widgets = {"motivo": forms.TextInput(attrs={"maxlength": 250})}
        help_texts = {"rut": "Ejemplo: 12.345.678-5 o 12345678-5."}

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'\-]+", nombre):
            raise forms.ValidationError("El nombre solamente puede contener letras, espacios, apóstrofes o guiones.")
        return nombre

    def clean_rut(self):
        return normalizar_rut(self.cleaned_data["rut"])

class EditarVisitaForm(VisitaForm):
    hora_salida = forms.DateTimeField(
        label="Fecha y hora de salida (opcional)",
        required=False, widget=FechaHoraWidget,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )

    class Meta(VisitaForm.Meta):
        fields = ("nombre", "rut", "motivo", "hora_entrada", "hora_salida")

    def clean(self):
        datos = super().clean()
        entrada, salida = datos.get("hora_entrada"), datos.get("hora_salida")
        if entrada and salida and salida < entrada:
            self.add_error("hora_salida", "La salida no puede ser anterior a la entrada.")
        return datos

class RegistrarSalidaForm(forms.ModelForm):
    hora_salida = forms.DateTimeField(
        label="Fecha y hora de salida (manual)",
        required=True, widget=FechaHoraWidget,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )

    class Meta:
        model = Visita
        fields = ("hora_salida",)

    def clean_hora_salida(self):
        fecha = self.cleaned_data["hora_salida"]
        if self.instance.hora_entrada and fecha < self.instance.hora_entrada:
            raise forms.ValidationError("La salida no puede ser anterior a la entrada.")
        return fecha


class StaffAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "Esta cuenta no tiene permiso de personal para gestionar visitas.", code="sin_permisos"
            )
