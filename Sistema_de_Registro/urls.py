from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import StaffAuthenticationForm

urlpatterns = [
    path("", views.registro_visitas, name="registro"),
    path("salida/<int:visita_id>/", views.registrar_salida, name="registrar_salida"),
    path("editar/<int:visita_id>/", views.editar_visita, name="editar_visita"),
    path("eliminar/<int:visita_id>/", views.eliminar_visita, name="eliminar_visita"),
    path("ingresar/", auth_views.LoginView.as_view(template_name="registros/login.html", authentication_form=StaffAuthenticationForm), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
]
