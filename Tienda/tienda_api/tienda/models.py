# tienda/models.py
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True)

    # Nuevos campos
    created_at = models.DateTimeField("Creado", default=timezone.now)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Nombre", max_length=150)
    slug = models.SlugField("Slug", max_length=180, unique=True)
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    description = models.TextField("Descripción", blank=True)
    image = models.ImageField("Imagen", upload_to="products/", blank=True, null=True)
    category = models.ForeignKey(
        Category, verbose_name="Categoría", on_delete=models.PROTECT
    )
    stock = models.PositiveIntegerField("Existencias", default=0)
    is_active = models.BooleanField("Activo", default=True)

    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

# tienda/models.py
class ContactMessage(models.Model):
    email = models.EmailField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

