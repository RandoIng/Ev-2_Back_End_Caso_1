import re
from django.core.exceptions import ValidationError


PATRON_SIN_PUNTOS = re.compile(r"^[0-9]{1,8}-?[0-9K]$")
PATRON_CON_PUNTOS = re.compile(r"^[0-9]{1,2}(?:\.[0-9]{3}){1,2}-[0-9K]$")


def normalizar_rut(valor):
    """Comprueba solo el formato y devuelve el RUT sin puntos, con guion y K mayúscula.

    No comprueba que el dígito verificador coincida con el cuerpo.
    """
    if not isinstance(valor, str):
        raise ValidationError("Ingrese un RUT en formato válido.")

    rut = valor.strip().upper()
    if not (PATRON_SIN_PUNTOS.fullmatch(rut) or PATRON_CON_PUNTOS.fullmatch(rut)):
        raise ValidationError(
            "Formato de RUT inválido. Ejemplo: 12.345.678-0 (DV: 0-9 o K)."
        )

    limpio = rut.replace(".", "").replace("-", "")
    cuerpo, dv = limpio[:-1], limpio[-1]
    return f"{int(cuerpo)}-{dv}"
