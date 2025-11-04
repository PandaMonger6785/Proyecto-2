from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

# DRF
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class HomeView(TemplateView):
    template_name = "home.html"

class AuthLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

class AuthLogoutView(LogoutView):
    pass

class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("home")
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# ===== API (DRF) =====
class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = ProductSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
