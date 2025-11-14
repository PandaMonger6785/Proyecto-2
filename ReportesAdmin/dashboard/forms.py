from django import forms


class ReportFilterForm(forms.Form):
    start_date = forms.DateField(
        label='Desde', required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label='Hasta', required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    product_name = forms.CharField(
        label='Producto', required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre contiene…'})
    )
    category = forms.CharField(
        label='Categoría', required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Categoría exacta'})
    )
    status = forms.ChoiceField(
        label='Estado', required=False,
        choices=(('', 'Todos'), ('pending', 'Pendiente'), ('received', 'Recibido'), ('return_requested', 'Devolución solicitada'))
    )