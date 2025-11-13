from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # Usa namespace "tienda" para que en plantillas funcione {% url 'tienda:...' %}
    path("", include(("tienda.urls", "tienda"), namespace="tienda")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
