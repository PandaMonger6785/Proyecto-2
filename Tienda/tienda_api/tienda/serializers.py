from rest_framework import serializers
from .models import Product, Category, Sale, SaleItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "description",
            "image",
            "category",
            "category_name",
            "stock",
            "is_active",
        )


# ---------- Ítems de venta (lectura/escritura en el mismo serializer) ----------
class SaleItemSerializer(serializers.ModelSerializer):
    # Escritura
    product_id = serializers.IntegerField(write_only=True, required=True)

    # Lectura “bonita”
    product_name  = serializers.CharField(source="product.name", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    subtotal      = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SaleItem
        fields = (
            "id",
            # write-only:
            "product_id",
            # read-only:
            "product_name",
            "category_name",
            "quantity",
            "unit_price",
            "status",
            "subtotal",
        )

    def get_subtotal(self, obj):
        return obj.subtotal  # asumiendo que tu modelo expone .subtotal (propiedad o @property)

    def validate(self, attrs):
        # Puedes forzar unit_price positivo, qty >=1, etc.
        qty = attrs.get("quantity", 0) or 0
        if qty <= 0:
            raise serializers.ValidationError({"quantity": "La cantidad debe ser mayor a cero."})
        return attrs


class SaleSerializer(serializers.ModelSerializer):
    # Acepta items con product_id al escribir, y devuelve nombres bonitos al leer
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ("id", "customer_name", "terms_accepted", "total_amount", "created_at", "items")
        read_only_fields = ("id", "total_amount", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        items_data = validated_data.pop("items", [])

        if not validated_data.get("terms_accepted"):
            raise serializers.ValidationError("Debes aceptar los términos y condiciones.")
        if not items_data:
            raise serializers.ValidationError("Debes seleccionar al menos un producto.")

        # Autocompletar customer_name si no vino
        if not validated_data.get("customer_name") and getattr(request, "user", None):
            u = request.user
            validated_data["customer_name"] = u.get_full_name() or u.get_username()

        sale = Sale.objects.create(user=getattr(request, "user", None), **validated_data)

        total = 0
        for item in items_data:
            prod_id    = item.pop("product_id")
            product    = Product.objects.get(pk=prod_id)
            quantity   = item.get("quantity", 1)
            unit_price = item.get("unit_price") or product.price  # fallback al precio del producto

            si = SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                status=item.get("status", SaleItem._meta.get_field("status").default),
            )
            total += si.subtotal  # asumiendo subtotal = quantity * unit_price

        sale.total_amount = total
        sale.save(update_fields=["total_amount"])
        return sale


class SaleItemStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ("status",)
