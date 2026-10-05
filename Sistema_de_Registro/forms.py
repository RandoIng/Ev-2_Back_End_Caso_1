import re

from django import forms
from .models import Visita

class VisitaForm(forms.ModelForm):

    class Meta:
        model = Visita
        fields = [
            "nombre",
            "rut",
            "motivo",
        ]

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()

        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )

        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'-]+$"

        if not re.match(patron, nombre):
            raise forms.ValidationError(
                "El nombre solamente puede contener letras."
            )

        return nombre

    def clean_rut(self):
        rut = self.cleaned_data["rut"].strip().upper()

        rut_limpio = rut.replace(".", "").replace("-", "")

        if len(rut_limpio) < 2:
            raise forms.ValidationError("Ingrese un RUT válido.")

        cuerpo = rut_limpio[:-1]
        dv_ingresado = rut_limpio[-1]

        if not cuerpo.isdigit():
            raise forms.ValidationError(
                "El RUT contiene caracteres inválidos."
            )

        if not (dv_ingresado.isdigit() or dv_ingresado == "K"):
            raise forms.ValidationError(
                "El dígito verificador no es válido."
            )

        suma = 0
        multiplicador = 2

        for numero in reversed(cuerpo):
            suma += int(numero) * multiplicador

            multiplicador += 1

            if multiplicador > 7:
                multiplicador = 2

        resto = suma % 11
        resultado = 11 - resto

        if resultado == 11:
            dv_calculado = "0"

        elif resultado == 10:
            dv_calculado = "K"

        else:
            dv_calculado = str(resultado)

        if dv_ingresado != dv_calculado:
            raise forms.ValidationError(
                "El RUT ingresado no es válido."
            )

        return f"{cuerpo}-{dv_ingresado}"