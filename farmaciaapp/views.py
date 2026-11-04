from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import LoginForm, MedicamentoForm, RegistroForm
from .models import Medicamento
from .serializers import MedicamentoSerializer


def es_administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


class IniciarSesionView(LoginView):

    template_name = "registration/login.html"
    authentication_form = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)


def inicio(request):
    total_medicamentos = Medicamento.objects.count()
    medicamentos_disponibles = Medicamento.objects.filter(stock__gt=0).count()

    contexto = {
        "total_medicamentos": total_medicamentos,
        "medicamentos_disponibles": medicamentos_disponibles,
    }
    return render(request, "farmaciaapp/inicio.html", contexto)


def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_staff = False
            usuario.is_superuser = False
            usuario.save()
            login(request, usuario)
            messages.success(
                request,
                "¡Tu cuenta fue creada correctamente! Ya puedes revisar nuestro inventario.",
            )
            return redirect("listar_medicamentos")
    else:
        form = RegistroForm()

    return render(request, "registration/registro.html", {"form": form})


@login_required
def listar_medicamentos(request):
    busqueda = request.GET.get("q", "").strip()
    medicamentos = Medicamento.objects.all()

    if busqueda:
        medicamentos = medicamentos.filter(
            Q(nombre__icontains=busqueda)
            | Q(laboratorio__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
        )

    contexto = {
        "medicamentos": medicamentos,
        "busqueda": busqueda,
        "total_medicamentos": Medicamento.objects.count(),
        "disponibles": Medicamento.objects.filter(stock__gt=0).count(),
        "con_receta": Medicamento.objects.filter(requiere_receta=True).count(),
        "stock_bajo": Medicamento.objects.filter(stock__lte=20).count(),
        "hoy": timezone.localdate(),
    }
    return render(request, "farmaciaapp/listar.html", contexto)


@user_passes_test(es_administrador, login_url="login")
def crear_medicamento(request):
    if request.method == "POST":
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            medicamento = form.save()
            messages.success(
                request,
                f'El medicamento "{medicamento.nombre}" fue agregado al inventario.',
            )
            return redirect("listar_medicamentos")
    else:
        form = MedicamentoForm()

    return render(
        request,
        "farmaciaapp/crear.html",
        {"form": form, "titulo": "Nuevo medicamento"},
    )


@user_passes_test(es_administrador, login_url="login")
def editar_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)

    if request.method == "POST":
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            medicamento = form.save()
            messages.success(
                request,
                f'El medicamento "{medicamento.nombre}" fue actualizado correctamente.',
            )
            return redirect("listar_medicamentos")
    else:
        form = MedicamentoForm(instance=medicamento)

    return render(
        request,
        "farmaciaapp/editar.html",
        {
            "form": form,
            "medicamento": medicamento,
            "titulo": "Editar medicamento",
        },
    )


@user_passes_test(es_administrador, login_url="login")
def eliminar_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)

    if request.method == "POST":
        nombre = medicamento.nombre
        medicamento.delete()
        messages.success(
            request, f'El medicamento "{nombre}" fue eliminado del inventario.'
        )
        return redirect("listar_medicamentos")

    return render(
        request,
        "farmaciaapp/eliminar.html",
        {"medicamento": medicamento},
    )


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def medicamentos_api(request):
    if request.method == "GET":
        medicamentos = Medicamento.objects.all()
        serializer = MedicamentoSerializer(medicamentos, many=True)
        return Response(serializer.data)

    serializer = MedicamentoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def medicamento_api_detalle(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)

    if request.method == "GET":
        serializer = MedicamentoSerializer(medicamento)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = MedicamentoSerializer(medicamento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    medicamento.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


obtener_token = obtain_auth_token
