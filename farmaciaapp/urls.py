from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        views.IniciarSesionView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="inicio"),
        name="logout",
    ),
    # Inventario web.
    path(
        "inventario/",
        views.listar_medicamentos,
        name="listar_medicamentos",
    ),
    path(
        "medicamentos/nuevo/",
        views.crear_medicamento,
        name="crear_medicamento",
    ),
    path(
        "medicamentos/<int:pk>/editar/",
        views.editar_medicamento,
        name="editar_medicamento",
    ),
    path(
        "medicamentos/<int:pk>/eliminar/",
        views.eliminar_medicamento,
        name="eliminar_medicamento",
    ),
    # API REST.
    path(
        "api/medicamentos/",
        views.medicamentos_api,
        name="api_medicamentos",
    ),
    path(
        "api/medicamentos/<int:pk>/",
        views.medicamento_api_detalle,
        name="api_medicamento_detalle",
    ),
    path("api/token/", views.obtener_token, name="api_token"),
]
