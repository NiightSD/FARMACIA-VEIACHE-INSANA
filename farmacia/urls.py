from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Farmacia Veiache · Administración"
admin.site.site_title = "Farmacia Veiache"
admin.site.index_title = "Panel de gestión"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("farmaciaapp.urls")),
]
