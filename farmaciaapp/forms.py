from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Medicamento


def _limites_fecha_vencimiento():
    hoy = timezone.localdate()
    try:
        limite = hoy.replace(year=hoy.year + 10)
    except ValueError:
        limite = hoy.replace(year=hoy.year + 10, day=28)
    return hoy, limite


class MedicamentoForm(forms.ModelForm):

    class Meta:
        model = Medicamento
        fields = [
            "nombre",
            "laboratorio",
            "precio",
            "stock",
            "descripcion",
            "requiere_receta",
            "fecha_vencimiento",
        ]
        labels = {
            "nombre": "Nombre del medicamento",
            "laboratorio": "Laboratorio",
            "precio": "Precio (CLP)",
            "stock": "Unidades en stock",
            "descripcion": "Descripción",
            "requiere_receta": "Requiere receta médica",
            "fecha_vencimiento": "Fecha de vencimiento",
        }
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Paracetamol 500 mg",
                    "autocomplete": "off",
                }
            ),
            "laboratorio": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Laboratorio Chile",
                    "autocomplete": "off",
                }
            ),
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "500000",
                    "step": "1",
                    "placeholder": "Ej: 2990",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "max": "10000",
                    "step": "1",
                    "placeholder": "Ej: 100",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Indicaciones, presentación y observaciones relevantes.",
                }
            ),
            "requiere_receta": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "fecha_vencimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy, limite = _limites_fecha_vencimiento()
        self.fields["fecha_vencimiento"].widget.attrs.update(
            {"min": hoy.isoformat(), "max": limite.isoformat()}
        )

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre debe tener al menos 3 caracteres."
            )
        return nombre

    def clean_laboratorio(self):
        return self.cleaned_data.get("laboratorio", "").strip()

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None or not 1 <= precio <= 500000:
            raise forms.ValidationError(
                "El precio debe estar entre 1 y 500.000 pesos."
            )
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is None or not 0 <= stock <= 10000:
            raise forms.ValidationError(
                "El stock debe estar entre 0 y 10.000 unidades."
            )
        return stock

    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get("fecha_vencimiento")
        if fecha is None:
            return fecha

        hoy, limite = _limites_fecha_vencimiento()
        if fecha < hoy:
            raise forms.ValidationError(
                "La fecha de vencimiento no puede ser anterior a hoy."
            )
        if fecha > limite:
            raise forms.ValidationError(
                "La fecha de vencimiento no puede superar los 10 años desde hoy."
            )
        return fecha


class RegistroForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        labels = {"username": "Nombre de usuario"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Elige un nombre de usuario",
                "autocomplete": "username",
                "autofocus": True,
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Crea una contraseña segura",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Repite tu contraseña",
                "autocomplete": "new-password",
            }
        )
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Tu nombre de usuario",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )
