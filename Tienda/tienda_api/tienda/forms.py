from django import forms


class ProductCreateForm(forms.Form):
    name = forms.CharField(max_length=150, label="Nombre")
    price = forms.DecimalField(max_digits=10, decimal_places=2, label="Precio")
    category_id = forms.IntegerField(min_value=1, label="Categoría (ID)")
    stock = forms.IntegerField(min_value=0, label="Stock", required=False)
    description = forms.CharField(widget=forms.Textarea, required=False, label="Descripción")


class ContactForm(forms.Form):
    email = forms.EmailField(label="Correo")
    comment = forms.CharField(widget=forms.Textarea, label="Comentario", max_length=2000)
