from django import forms

class ProductCreateForm(forms.Form):
    name        = forms.CharField(max_length=150, label="Nombre")
    slug        = forms.SlugField(max_length=160, required=False, label="Slug (opcional)")
    price       = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, label="Precio (MXN)")
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":4}), required=False, label="Descripción")
    category    = forms.CharField(max_length=50, required=False, label="Categoría (ej. tecno, hogar)")
    stock       = forms.IntegerField(min_value=0, initial=0, label="Stock")
    is_active   = forms.BooleanField(required=False, initial=True, label="Activo")
    image_file  = forms.ImageField(required=False, label="Imagen (subir)")

