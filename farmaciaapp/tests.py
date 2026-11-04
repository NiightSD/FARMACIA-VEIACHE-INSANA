from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .forms import MedicamentoForm
from .models import Medicamento
from .serializers import MedicamentoSerializer


def datos_medicamento(**cambios):
    """Datos válidos reutilizables para pruebas de formularios y API."""
    datos = {
        "nombre": "Paracetamol 500 mg",
        "laboratorio": "Laboratorio Chile",
        "precio": 2990,
        "stock": 100,
        "descripcion": "Analgésico y antipirético.",
        "requiere_receta": False,
        "fecha_vencimiento": timezone.localdate() + timedelta(days=365),
    }
    datos.update(cambios)
    return datos


class ValidacionFormularioTests(TestCase):
    def test_formulario_valido(self):
        form = MedicamentoForm(data=datos_medicamento())
        self.assertTrue(form.is_valid(), form.errors)

    def test_nombre_debe_tener_al_menos_tres_caracteres(self):
        form = MedicamentoForm(data=datos_medicamento(nombre="Ab"))
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)

    def test_precio_debe_estar_en_rango(self):
        for precio in (0, 500001):
            with self.subTest(precio=precio):
                form = MedicamentoForm(data=datos_medicamento(precio=precio))
                self.assertFalse(form.is_valid())
                self.assertIn("precio", form.errors)

    def test_stock_debe_estar_en_rango(self):
        for stock in (-1, 10001):
            with self.subTest(stock=stock):
                form = MedicamentoForm(data=datos_medicamento(stock=stock))
                self.assertFalse(form.is_valid())
                self.assertIn("stock", form.errors)

    def test_fecha_no_puede_ser_pasada(self):
        form = MedicamentoForm(
            data=datos_medicamento(
                fecha_vencimiento=timezone.localdate() - timedelta(days=1)
            )
        )
        self.assertFalse(form.is_valid())
        self.assertIn("fecha_vencimiento", form.errors)

    def test_fecha_no_puede_superar_diez_anios(self):
        hoy = timezone.localdate()
        try:
            fecha_excedida = hoy.replace(year=hoy.year + 11)
        except ValueError:
            fecha_excedida = hoy.replace(year=hoy.year + 11, day=28)
        form = MedicamentoForm(
            data=datos_medicamento(fecha_vencimiento=fecha_excedida)
        )
        self.assertFalse(form.is_valid())
        self.assertIn("fecha_vencimiento", form.errors)


class ValidacionSerializerTests(TestCase):
    def test_serializer_acepta_datos_validos(self):
        serializer = MedicamentoSerializer(data=datos_medicamento())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rechaza_reglas_de_negocio(self):
        serializer = MedicamentoSerializer(
            data=datos_medicamento(nombre="AB", precio=0, stock=10001)
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("nombre", serializer.errors)
        self.assertIn("precio", serializer.errors)
        self.assertIn("stock", serializer.errors)

    def test_serializer_rechaza_fecha_fuera_de_rango(self):
        serializer = MedicamentoSerializer(
            data=datos_medicamento(
                fecha_vencimiento=timezone.localdate() - timedelta(days=1)
            )
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("fecha_vencimiento", serializer.errors)


class VistasWebTests(TestCase):
    def setUp(self):
        self.cliente = User.objects.create_user(
            username="cliente", password="ClaveSegura123"
        )
        self.staff = User.objects.create_user(
            username="staff", password="ClaveSegura123", is_staff=True
        )
        self.medicamento = Medicamento.objects.create(**datos_medicamento())

    def test_inicio_es_publico(self):
        response = self.client.get(reverse("inicio"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Farmacia Veiache")

    def test_inventario_requiere_autenticacion(self):
        response = self.client.get(reverse("listar_medicamentos"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_cliente_puede_ver_inventario_sin_acciones_de_gestion(self):
        self.client.force_login(self.cliente)
        response = self.client.get(reverse("listar_medicamentos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.medicamento.nombre)
        self.assertNotContains(response, reverse("crear_medicamento"))
        self.assertNotContains(
            response, reverse("editar_medicamento", args=[self.medicamento.pk])
        )
        self.assertNotContains(
            response, reverse("eliminar_medicamento", args=[self.medicamento.pk])
        )

    def test_staff_ve_acciones_de_gestion(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("listar_medicamentos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("crear_medicamento"))
        self.assertContains(
            response, reverse("editar_medicamento", args=[self.medicamento.pk])
        )
        self.assertContains(
            response, reverse("eliminar_medicamento", args=[self.medicamento.pk])
        )

    def test_cliente_no_puede_acceder_a_vistas_administrativas(self):
        self.client.force_login(self.cliente)
        urls = [
            reverse("crear_medicamento"),
            reverse("editar_medicamento", args=[self.medicamento.pk]),
            reverse("eliminar_medicamento", args=[self.medicamento.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_cliente_no_cae_en_bucle_al_intentar_acceder_como_staff(self):
        self.client.force_login(self.cliente)
        response = self.client.get(reverse("crear_medicamento"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][0], reverse("inicio"))
        self.assertNotContains(response, "Información del medicamento")

    def test_usuario_autenticado_es_redirigido_al_inicio_desde_login(self):
        self.client.force_login(self.cliente)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("inicio"))

    def test_cerrar_sesion_redirige_al_inicio(self):
        self.client.force_login(self.cliente)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_staff_puede_crear_medicamento(self):
        self.client.force_login(self.staff)
        datos = datos_medicamento(nombre="Ibuprofeno 400 mg")
        response = self.client.post(reverse("crear_medicamento"), datos)
        self.assertRedirects(response, reverse("listar_medicamentos"))
        self.assertTrue(
            Medicamento.objects.filter(nombre="Ibuprofeno 400 mg").exists()
        )

    def test_staff_puede_eliminar_medicamento_solo_por_post(self):
        self.client.force_login(self.staff)
        url = reverse("eliminar_medicamento", args=[self.medicamento.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Medicamento.objects.filter(pk=self.medicamento.pk).exists())

    def test_registro_crea_cliente_sin_privilegios(self):
        response = self.client.post(
            reverse("registro"),
            {
                "username": "nuevo_cliente",
                "password1": "UnaClaveMuySegura987",
                "password2": "UnaClaveMuySegura987",
            },
        )
        self.assertRedirects(response, reverse("listar_medicamentos"))
        usuario = get_user_model().objects.get(username="nuevo_cliente")
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)


class TokenAutomaticoTests(TestCase):
    def test_token_se_crea_al_crear_un_usuario(self):
        usuario = User.objects.create_user(
            username="cliente_token", password="ClaveSegura123"
        )
        self.assertTrue(Token.objects.filter(user=usuario).exists())

    def test_token_se_crea_al_crear_un_superusuario(self):
        usuario = User.objects.create_superuser(
            username="admin_token",
            email="admin_token@example.com",
            password="ClaveSegura123",
        )
        self.assertTrue(Token.objects.filter(user=usuario).exists())

    def test_no_se_duplica_el_token_al_guardar_el_usuario(self):
        usuario = User.objects.create_user(
            username="cliente_token", password="ClaveSegura123"
        )
        usuario.first_name = "Cliente"
        usuario.save()
        self.assertEqual(Token.objects.filter(user=usuario).count(), 1)

    def test_comando_genera_tokens_faltantes(self):
        usuario = User.objects.create_user(
            username="cliente_sin_token", password="ClaveSegura123"
        )
        Token.objects.filter(user=usuario).delete()
        self.assertFalse(Token.objects.filter(user=usuario).exists())

        call_command("generar_tokens")

        self.assertTrue(Token.objects.filter(user=usuario).exists())


class APIMedicamentosTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="api_user", password="ClaveSegura123"
        )
        self.token = Token.objects.get(user=self.usuario)
        self.api = APIClient()
        self.medicamento = Medicamento.objects.create(**datos_medicamento())
        self.url_lista = reverse("api_medicamentos")
        self.url_detalle = reverse(
            "api_medicamento_detalle", args=[self.medicamento.pk]
        )

    def autenticar(self):
        self.api.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_api_rechaza_acceso_sin_token(self):
        self.assertEqual(self.api.get(self.url_lista).status_code, 401)

    def test_api_lista_con_token(self):
        self.autenticar()
        response = self.api.get(self.url_lista)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre"], self.medicamento.nombre)

    def test_api_crear_actualizar_y_eliminar(self):
        self.autenticar()
        datos = datos_medicamento(nombre="Amoxicilina 500 mg", requiere_receta=True)
        datos["fecha_vencimiento"] = datos["fecha_vencimiento"].isoformat()

        crear = self.api.post(self.url_lista, datos, format="json")
        self.assertEqual(crear.status_code, 201)
        nuevo_id = crear.data["id"]

        datos["precio"] = 4500
        actualizar = self.api.put(
            reverse("api_medicamento_detalle", args=[nuevo_id]),
            datos,
            format="json",
        )
        self.assertEqual(actualizar.status_code, 200)
        self.assertEqual(actualizar.data["precio"], 4500)

        eliminar = self.api.delete(
            reverse("api_medicamento_detalle", args=[nuevo_id])
        )
        self.assertEqual(eliminar.status_code, 204)
        self.assertFalse(Medicamento.objects.filter(pk=nuevo_id).exists())

    def test_api_valida_reglas_de_negocio(self):
        self.autenticar()
        datos = datos_medicamento(
            nombre="AB",
            precio=500001,
            stock=-1,
            fecha_vencimiento=(timezone.localdate() - timedelta(days=1)).isoformat(),
        )
        response = self.api.post(self.url_lista, datos, format="json")
        self.assertEqual(response.status_code, 400)
        for campo in ("nombre", "precio", "stock", "fecha_vencimiento"):
            self.assertIn(campo, response.data)

    def test_endpoint_obtiene_token(self):
        response = self.api.post(
            reverse("api_token"),
            {"username": "api_user", "password": "ClaveSegura123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
