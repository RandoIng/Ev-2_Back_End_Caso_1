from django.core.exceptions import ValidationError
from django.db import models
from .rut import normalizar_rut

class Visita(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)
    motivo = models.CharField(max_length=250)
    # Hora manual: se elimina auto_now_add; no se toma el reloj del servidor.
    hora_entrada = models.DateTimeField(verbose_name="Fecha y hora de entrada")
    hora_salida = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y hora de salida")

    class Meta:
        ordering = ["-hora_entrada"]
        verbose_name = "visita"
        verbose_name_plural = "visitas"

    def clean(self):
        super().clean()
        self.rut = normalizar_rut(self.rut)
        if self.hora_entrada and self.hora_salida and self.hora_salida < self.hora_entrada:
            raise ValidationError({"hora_salida": "La salida no puede ser anterior a la entrada."})

    def __str__(self):
        return f"{self.nombre} - {self.rut}"
