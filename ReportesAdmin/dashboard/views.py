from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import F, Sum
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View

from tienda.models import SaleItem

from .forms import ReportFilterForm
from .pdf import generate_report_pdf


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('dashboard:login')

    def test_func(self):  # type: ignore[override]
        return self.request.user.is_staff


class DashboardLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:reportes')


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard:login')


class ReportView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/reportes.html'

    def get_form(self):
        return ReportFilterForm(self.request.GET or None)

    def filter_queryset(self, qs, data):
        if data.get('start_date'):
            qs = qs.filter(sale__created_at__date__gte=data['start_date'])
        if data.get('end_date'):
            qs = qs.filter(sale__created_at__date__lte=data['end_date'])
        if data.get('product_name'):
            qs = qs.filter(product_name__icontains=data['product_name'])
        if data.get('category'):
            qs = qs.filter(category_name__iexact=data['category'])
        if data.get('status'):
            qs = qs.filter(status=data['status'])
        return qs

    def get_queryset(self, form: ReportFilterForm):
        qs = SaleItem.objects.select_related('sale').order_by('-sale__created_at')
        if not form.is_valid():
            return qs.none()
        return self.filter_queryset(qs, form.cleaned_data)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = self.get_form()
        items = self.get_queryset(form)
        totals = items.aggregate(
            total_amount=Sum(F('quantity') * F('unit_price')),
            total_qty=Sum('quantity'),
        )
        ctx.update({
            'form': form,
            'items': items,
            'total_amount': totals.get('total_amount') or 0,
            'total_qty': totals.get('total_qty') or 0,
        })
        return ctx


class ReportPdfView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ReportFilterForm(request.GET or None)
        base_qs = SaleItem.objects.select_related('sale').order_by('-sale__created_at')
        if form.is_valid():
            items = ReportView().filter_queryset(base_qs, form.cleaned_data)
        else:
            items = base_qs.none()
        totals = items.aggregate(
            total_amount=Sum(F('quantity') * F('unit_price')),
            total_qty=Sum('quantity'),
        )
        filters = {k: v for k, v in form.cleaned_data.items() if v} if form.is_valid() else {}
        pdf_bytes = generate_report_pdf(
            title='Reporte de ventas',
            filters=filters,
            rows=items,
            summary={'total': totals.get('total_amount') or 0, 'cantidad': totals.get('total_qty') or 0},
        )
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'
        return response