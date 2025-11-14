from django.urls import path
from .views import ReportView, ReportPdfView, DashboardLoginView, DashboardLogoutView

app_name = 'dashboard'

urlpatterns = [
    path('login/', DashboardLoginView.as_view(), name='login'),
    path('logout/', DashboardLogoutView.as_view(), name='logout'),
    path('', ReportView.as_view(), name='reportes'),
    path('descargar/', ReportPdfView.as_view(), name='descargar_pdf'),
]