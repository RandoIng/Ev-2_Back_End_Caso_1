from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import VisitaForm
from .models import Visita


def registro_visitas(request):

    if request.method == "POST":

        form = VisitaForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("registro")

    else:

        form = VisitaForm()


    fecha_actual = timezone.localdate()


    visitas = Visita.objects.filter(
        hora_entrada__date=fecha_actual
    ).order_by("-hora_entrada")

    contexto = {
        "form": form,
        "visitas": visitas,
        "fecha_actual": fecha_actual,
    }

    return render(
        request,
        "registros/registro.html",
        contexto
    )


def registrar_salida(request, visita_id):

    visita = get_object_or_404(
        Visita,
        id=visita_id
    )

    if request.method == "POST":

        if visita.hora_salida is None:

            visita.hora_salida = timezone.now()

            visita.save(
                update_fields=["hora_salida"]
            )

    return redirect("registro")
