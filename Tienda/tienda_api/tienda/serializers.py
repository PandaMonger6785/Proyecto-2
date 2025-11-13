from django.db import transaction
from rest_framework import serializers

from .models import Category, Product, Sale, SaleItem


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


class SaleItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True, required=True)
    product_name = serializers.CharField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SaleItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "category_name",
            "quantity",
            "unit_price",
            "status",
            "subtotal",
        )
        read_only_fields = ("id", "product_name", "category_name", "subtotal")

    def get_subtotal(self, obj):
        return obj.subtotal

    def validate(self, attrs):
        quantity = attrs.get("quantity", 0) or 0
        if quantity <= 0:
            raise serializers.ValidationError({"quantity": "La cantidad debe ser mayor a cero."})

        unit_price = attrs.get("unit_price")
        if unit_price is not None and unit_price <= 0:
            raise serializers.ValidationError({"unit_price": "El precio debe ser mayor a cero."})

        return attrs


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ("id", "customer_name", "terms_accepted", "total_amount", "created_at", "items")
        read_only_fields = ("id", "total_amount", "created_at")

    def create(self, validated_data):
        request = self.context.get("request")
        items_data = validated_data.pop("items", [])

        if not validated_data.get("terms_accepted"):
            raise serializers.ValidationError({"terms_accepted": "Debes aceptar los términos y condiciones."})

        if not items_data:
            raise serializers.ValidationError({"items": "Debes seleccionar al menos un producto."})

        if not validated_data.get("customer_name"):
            user = getattr(request, "user", None)
            if user is not None and getattr(user, "is_authenticated", False):
                validated_data["customer_name"] = user.get_full_name() or user.get_username()
            else:
                validated_data["customer_name"] = "Cliente"

        user_for_sale = None
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            user_for_sale = request.user

        with transaction.atomic():
            sale = Sale.objects.create(user=user_for_sale, **validated_data)
            total = 0

            for item in items_data:
                product_id = item.get("product_id")
                try:
                    product = Product.objects.get(pk=product_id, is_active=True)
                except Product.DoesNotExist as exc:
                    raise serializers.ValidationError(
                        {"items": f"Producto con id {product_id} no existe o está inactivo."}
                    ) from exc

                quantity = item.get("quantity", 1)
                unit_price = item.get("unit_price") or product.price
                status = item.get("status", SaleItem._meta.get_field("status").default)

                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product_name=product.name,
                    category_name=product.category.name if product.category_id else "",
                    quantity=quantity,
                    unit_price=unit_price,
                    status=status,
                )
                total += sale_item.subtotal

            sale.total_amount = total
            sale.save(update_fields=["total_amount"])

        return sale


class SaleItemStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Sale.STATUS_CHOICES)

    class Meta:
        model = SaleItem
        fields = ("status",)