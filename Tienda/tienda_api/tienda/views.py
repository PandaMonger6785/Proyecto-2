from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .forms import ContactForm
from .models import Category, Product, Sale, SaleItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    SaleItemStatusSerializer,
    SaleSerializer,
)


class HomeView(TemplateView):
    template_name = "home.html"

class ContactView(LoginRequiredMixin, FormView):
    template_name = "contacto.html"
    form_class = ContactForm
    success_url = reverse_lazy("tienda:contacto")
    login_url = "tienda:login"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return f"{super().get_success_url()}?success=1"

class SalesView(LoginRequiredMixin, TemplateView):
    template_name = "ventas.html"
    login_url = "tienda:login"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["products"] = Product.objects.filter(is_active=True).order_by("name")
        ctx["status_choices"] = dict(Sale.STATUS_CHOICES)
        return ctx

class AuthLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

class AuthLogoutView(LogoutView):
    next_page = reverse_lazy("tienda:home")

class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("tienda:login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)




class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = ProductSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Sale.objects.filter(user=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        read_serializer = self.get_serializer(sale)
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SaleItemViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = SaleItemStatusSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "head", "options"]

    def get_queryset(self):
        return SaleItem.objects.filter(sale__user=self.request.user)
