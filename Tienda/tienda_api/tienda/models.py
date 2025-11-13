from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True)
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
    category = models.ForeignKey(Category, verbose_name="Categoría", on_delete=models.PROTECT)
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


class ContactMessage(models.Model):
    email = models.EmailField("Correo")
    comment = models.TextField("Comentario")
    created_at = models.DateTimeField("Enviado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"Mensaje de {self.email}"


class Sale(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("received", "Recibido"),
        ("return_requested", "Devolución solicitada"),
    )

    user = models.ForeignKey(
        User,
        verbose_name="Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
    )
    customer_name = models.CharField("Cliente", max_length=150)
    terms_accepted = models.BooleanField("Aceptó términos", default=False)
    total_amount = models.DecimalField("Total", max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

    def __str__(self):
        return f"Venta #{self.pk}"

    def recalc_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=["total_amount"])


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Venta",
    )
    product_name = models.CharField("Producto", max_length=200)
    category_name = models.CharField("Categoría", max_length=120, blank=True)
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    unit_price = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Sale.STATUS_CHOICES,
        default="pending",
    )
    status_updated_at = models.DateTimeField("Actualizado", auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Artículo de venta"
        verbose_name_plural = "Artículos de venta"

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def mark_received(self):
        self.status = "received"
        self.save(update_fields=["status", "status_updated_at"])

    def request_return(self):
        self.status = "return_requested"
        self.save(update_fields=["status", "status_updated_at"])