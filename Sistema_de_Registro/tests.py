from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import VisitaForm, RegistrarSalidaForm
from .models import Visita
from .rut import normalizar_rut


class RutTests(TestCase):
    def test_formatos_correctos(self):
        for rut in ("12.345.678-5", "12345678-5", "123456785", "12.345.678-5 "):
            with self.subTest(rut=rut):
                self.assertEqual(normalizar_rut(rut), "12345678-5")

    def test_rut_con_k(self):
        self.assertEqual(normalizar_rut("6-K"), "6-K")

    def test_rechazar_rut_incorrecto(self):
        for rut in ("12.345.678-9", "12..345.678-5", "0-0", "12-34-5678-5", "", "12345678A", "12 345 678-5"):
            with self.subTest(rut=rut), self.assertRaises(ValidationError):
                normalizar_rut(rut)


class RegistroTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("guardia", password="clave_de_prueba", is_staff=True)
        self.entrada = timezone.localtime(timezone.now()).replace(hour=9, minute=0, second=0, microsecond=0)
        self.entrada = self.entrada - timedelta(days=1)
        self.entrada_str = self.entrada.strftime("%Y-%m-%dT%H:%M")

    def test_requiere_personal_autorizado(self):
        respuesta = self.client.get(reverse("registro"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("ingresar", respuesta.url)

    def test_crear_y_almacenar_rut_normalizado(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("registro"), {
            "nombre": "Ana Perez",
            "rut": "12.345.678-5",
            "motivo": "Reunion",
            "hora_entrada": self.entrada_str,
        })
        self.assertRedirects(response, reverse("registro"))
        visita = Visita.objects.get()
        self.assertEqual(visita.rut, "12345678-5")
        self.assertIsNone(visita.hora_salida)

    def test_rechazar_dv_invalido(self):
        formulario = VisitaForm(data={
            "nombre": "Ana Perez", "rut": "12.345.678-9",
            "motivo": "Reunion", "hora_entrada": self.entrada_str,
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn("rut", formulario.errors)

    def test_salida_anterior_a_entrada_invalida(self):
        visita = Visita.objects.create(
            nombre="Ana Perez", rut="12345678-5", motivo="Reunion", hora_entrada=self.entrada,
        )
        salida_anterior = (self.entrada - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        formulario = RegistrarSalidaForm(data={"hora_salida": salida_anterior}, instance=visita)
        self.assertFalse(formulario.is_valid())

    def test_registrar_salida_manual(self):
        self.client.force_login(self.user)
        visita = Visita.objects.create(
            nombre="Ana Perez", rut="12345678-5", motivo="Reunion", hora_entrada=self.entrada,
        )
        salida = (self.entrada + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(reverse("registrar_salida", args=[visita.pk]), {"hora_salida": salida})
        self.assertRedirects(response, reverse("registro"))
        visita.refresh_from_db()
        self.assertIsNotNone(visita.hora_salida)
        self.assertEqual(timezone.localtime(visita.hora_salida).strftime("%Y-%m-%dT%H:%M"), salida)

    def test_historico_se_muestra_aunque_no_sea_hoy(self):
        self.client.force_login(self.user)
        Visita.objects.create(nombre="Ana Perez", rut="12345678-5", motivo="Reunion", hora_entrada=self.entrada)
        response = self.client.get(reverse("registro"))
        self.assertContains(response, "Ana Perez")

    def test_eliminar_requiere_post(self):
        self.client.force_login(self.user)
        visita = Visita.objects.create(nombre="Ana Perez", rut="12345678-5", motivo="Reunion", hora_entrada=self.entrada)
        self.client.get(reverse("eliminar_visita", args=[visita.pk]))
        self.assertTrue(Visita.objects.filter(pk=visita.pk).exists())
        self.client.post(reverse("eliminar_visita", args=[visita.pk]))
        self.assertFalse(Visita.objects.filter(pk=visita.pk).exists())
