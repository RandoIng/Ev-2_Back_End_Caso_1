from datetime import date
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import VisitaForm, EditarVisitaForm, RegistrarSalidaForm
from .models import Visita

@staff_member_required(login_url="login")
def registro_visitas(request):
    if request.method == "POST":
        form = VisitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Visita registrada correctamente.")
            return redirect("registro")
        messages.error(request, "Corrige los campos señalados en el formulario.")
    else:
        form = VisitaForm()

    visitas = Visita.objects.all().order_by("-hora_entrada", "-pk")
    fecha_filtro = request.GET.get("fecha", "")
    estado_filtro = request.GET.get("estado", "")
    if fecha_filtro:
        try:
            date.fromisoformat(fecha_filtro)
            visitas = visitas.filter(hora_entrada__date=fecha_filtro)
        except ValueError:
            messages.warning(request, "El filtro de fecha no es válido.")
            fecha_filtro = ""
    if estado_filtro == "abierta":
        visitas = visitas.filter(hora_salida__isnull=True)
    elif estado_filtro == "finalizada":
        visitas = visitas.filter(hora_salida__isnull=False)
    else:
        estado_filtro = ""
    pagina = Paginator(visitas, 10).get_page(request.GET.get("pagina"))
    return render(request, "registros/registro.html", {
        "form": form, "pagina": pagina,
        "fecha_filtro": fecha_filtro, "estado_filtro": estado_filtro,
    })

@staff_member_required(login_url="login")
@require_POST
def registrar_salida(request, visita_id):
    visita = get_object_or_404(Visita, pk=visita_id)
    if visita.hora_salida is not None:
        messages.warning(request, "La visita ya tiene una salida registrada.")
        return redirect("registro")
    form = RegistrarSalidaForm(request.POST, instance=visita)
    if form.is_valid():
        form.save()
        messages.success(request, "Salida registrada correctamente.")
    else:
        errores = "; ".join(str(e) for lista in form.errors.values() for e in lista)
        messages.error(request, errores or "Fecha y hora de salida inválidas.")
    return redirect("registro")

@staff_member_required(login_url="login")
def editar_visita(request, visita_id):
    visita = get_object_or_404(Visita, pk=visita_id)
    form = EditarVisitaForm(request.POST if request.method == "POST" else None, instance=visita)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Visita actualizada correctamente.")
        return redirect("registro")
    return render(request, "registros/editar.html", {"form": form, "visita": visita})

@staff_member_required(login_url="login")
def eliminar_visita(request, visita_id):
    visita = get_object_or_404(Visita, pk=visita_id)
    if request.method == "POST":
        visita.delete()
        messages.success(request, "Visita eliminada correctamente.")
        return redirect("registro")
    return render(request, "registros/eliminar.html", {"visita": visita})
