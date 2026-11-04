# Farmacia_app-EVA3

Aplicación web de gestión farmacéutica desarrollada con Django 5, MySQL y
Django REST Framework. El sitio público, el inventario para clientes y el panel
de administración comparten una interfaz responsive construida con Bootstrap 5
y un tema visual verde.

## Características

- Página de inicio pública con identidad visual de **Farmacia Veiache**.
- Registro e inicio de sesión de clientes.
- Inventario visible solo para usuarios autenticados y en modo lectura.
- Gestión de medicamentos (crear, editar y eliminar) exclusiva para personal
  con `is_staff=True` o `is_superuser=True`.
- Validaciones de negocio aplicadas tanto en la web como en la API.
- API REST protegida con tokens para consultar, crear, actualizar y eliminar
  medicamentos.
- Navbar dinámico que adapta sus acciones según la sesión y el rol.

## Requisitos

- **Python 3.10 a 3.12** (recomendado: 3.12, compatible con Django 5.0.14).
- MySQL / MariaDB en ejecución en `localhost:3306`.
- Las dependencias exactas del proyecto:

```text
asgiref==3.12.1
Django==5.0.14
mysqlclient==2.3.0
sqlparse==0.6.0
tzdata==2026.5
djangorestframework==3.15.2
```

## Estructura principal

```text
Farmacia_app-EVA3/
├── manage.py
├── requirements.txt
├── farmacia/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── farmaciaapp/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── generar_tokens.py
│   ├── migrations/
│   └── templates/
│       ├── farmaciaapp/
│       │   ├── base.html
│       │   ├── crear.html
│       │   ├── editar.html
│       │   ├── eliminar.html
│       │   ├── inicio.html
│       │   └── listar.html
│       └── registration/
│           ├── login.html
│           └── registro.html
└── static/farmaciaapp/
    ├── css/estilos.css
    └── img/favicon.svg
```

## Instalación

1. Crear y activar un entorno virtual con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. Crear la base de datos MySQL. La configuración utiliza el usuario `root`,
   el puerto `3306` y la contraseña vacía por defecto:

```sql
CREATE DATABASE IF NOT EXISTS farmacia_bd
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

También se puede crear desde la terminal:

```powershell
mysql -u root -e "CREATE DATABASE IF NOT EXISTS farmacia_bd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Si el usuario `root` tiene contraseña, expórtala antes de ejecutar Django:

```powershell
$env:DB_PASSWORD = "tu_contraseña"
```

3. Aplicar las migraciones y crear un administrador:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Iniciar el servidor:

```powershell
python manage.py runserver
```

La aplicación estará disponible en <http://127.0.0.1:8000/>.

## Rutas web

| Ruta | Descripción | Acceso |
| --- | --- | --- |
| `/` | Página de inicio | Público |
| `/login/` | Inicio de sesión | Público |
| `/registro/` | Registro de clientes | Público |
| `/inventario/` | Inventario en modo lectura | Usuarios autenticados |
| `/medicamentos/nuevo/` | Crear medicamento | Staff / superusuario |
| `/medicamentos/<id>/editar/` | Editar medicamento | Staff / superusuario |
| `/medicamentos/<id>/eliminar/` | Eliminar medicamento | Staff / superusuario |
| `/admin/` | Administración de Django | Staff / superusuario |

Los usuarios creados desde el formulario de registro siempre se guardan con
`is_staff=False` e `is_superuser=False`.

## API REST

La API usa `TokenAuthentication` e `IsAuthenticated` en todos sus endpoints de
medicamentos.

Los tokens se crean automáticamente al registrar un usuario, al usar
`python manage.py createsuperuser` y al crear usuarios desde el panel de
administración. Si ya existen usuarios sin token —por ejemplo, creados antes de
activar esta función— se pueden completar con:

```powershell
python manage.py generar_tokens
```

El comando es idempotente: no duplica los tokens que ya existen. También se
puede solicitar el token de un usuario concreto mediante el endpoint:

Obtener un token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario", "password": "contraseña"}'
```

Respuesta:

```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

Endpoints:

| Método | Ruta | Acción |
| --- | --- | --- |
| `GET` | `/api/medicamentos/` | Lista los medicamentos |
| `POST` | `/api/medicamentos/` | Crea un medicamento |
| `GET` | `/api/medicamentos/<id>/` | Obtiene un medicamento |
| `PUT` | `/api/medicamentos/<id>/` | Actualiza un medicamento |
| `DELETE` | `/api/medicamentos/<id>/` | Elimina un medicamento |

Ejemplo de creación:

```bash
curl -X POST http://127.0.0.1:8000/api/medicamentos/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Paracetamol 500 mg",
    "laboratorio": "Laboratorio Chile",
    "precio": 2990,
    "stock": 100,
    "descripcion": "Analgésico y antipirético.",
    "requiere_receta": false,
    "fecha_vencimiento": "2027-12-31"
  }'
```

## Reglas de validación

Se aplican en `forms.py` y `serializers.py`:

- Nombre: mínimo 3 caracteres.
- Precio: entre 1 y 500.000 pesos.
- Stock: entre 0 y 10.000 unidades.
- Fecha de vencimiento: desde hoy hasta un máximo de 10 años en el futuro.

## Pruebas

Las pruebas cubren validaciones, permisos web, registro, navbar por rol, token y
operaciones CRUD de la API:

```powershell
python manage.py test farmaciaapp
```

MySQL debe permitir crear la base de datos de pruebas (`test_farmacia_bd`).
