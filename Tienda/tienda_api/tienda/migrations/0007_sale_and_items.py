from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0006_contactmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=150, verbose_name='Cliente')),
                ('terms_accepted', models.BooleanField(default=False, verbose_name='Aceptó términos')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Venta',
                'verbose_name_plural': 'Ventas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200, verbose_name='Producto')),
                ('category_name', models.CharField(blank=True, max_length=120, verbose_name='Categoría')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio unitario')),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('received', 'Recibido'), ('return_requested', 'Devolución solicitada')], default='pending', max_length=20, verbose_name='Estado')),
                ('status_updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Actualizado')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='tienda.sale', verbose_name='Venta')),
            ],
            options={
                'verbose_name': 'Artículo de venta',
                'verbose_name_plural': 'Artículos de venta',
            },
        ),
    ]