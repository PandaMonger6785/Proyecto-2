# tienda/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category


# ===== Helpers =====
def safe_image_url(obj) -> str:
    """
    Devuelve la URL de la imagen solo si realmente hay un archivo.
    Evita ValueError cuando no hay imagen asociada.
    """
    f = getattr(obj, "image", None)
    if not f:
        return ""
    # si no tiene nombre, no intentamos acceder a .url
    if not getattr(f, "name", ""):
        return ""
    try:
        return f.url
    except Exception:
        return ""


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # columnas de la tabla
    list_display = (
        "thumb",           # miniatura segura
        "name",
        "category",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_display_links = ("name",)
    list_editable = ("is_active",)   # edita rápido desde la lista
    list_per_page = 25

    # filtros y búsqueda
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "slug", "description", "category__name")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # autocompletar y solo-lectura
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at", "image_preview")

    # llena slug desde name
    prepopulated_fields = {"slug": ("name",)}

    # secciones del formulario
    fieldsets = (
        ("Datos básicos", {"fields": ("name", "slug", "price", "description")}),
        ("Imagen", {"fields": ("image", "image_preview")}),
        ("Clasificación", {"fields": ("category",)}),
        ("Inventario y estado", {"fields": ("stock", "is_active")}),
        ("Metadatos", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    # ----- helpers de UI (seguros) -----
    @admin.display(description="Imagen")
    def thumb(self, obj):
        """Miniatura en la lista (segura si no hay archivo)."""
        url = safe_image_url(obj)
        if url:
            return format_html('<img src="{}" style="height:40px;border-radius:6px">', url)
        return "—"

    @admin.display(description="Vista previa")
    def image_preview(self, obj):
        """Vista previa grande en el formulario (segura si no hay archivo)."""
        url = safe_image_url(obj)
        if url:
            return format_html('<img src="{}" style="max-height:240px;border-radius:10px">', url)
        return "Sin imagen"

    # ----- acciones masivas -----
    @admin.action(description="Marcar como Activo")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} producto(s) marcados como activos.")

    @admin.action(description="Marcar como Inactivo")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} producto(s) marcados como inactivos.")

    actions = ["make_active", "make_inactive"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Nota: asegúrate de que tu modelo Category tenga created_at.
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}

