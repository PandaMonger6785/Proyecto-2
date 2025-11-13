from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthLoginView,
    AuthLogoutView,
    CategoryViewSet,
    ContactView,
    HomeView,
    ProductViewSet,
    SaleItemViewSet,
    SalesView,
    SaleViewSet,
    SignUpView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'sale-items', SaleItemViewSet, basename='sale-item')

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("contacto/", ContactView.as_view(), name="contacto"),
    path("ventas/", SalesView.as_view(), name="ventas"),
    path("login/", AuthLoginView.as_view(), name="login"),
    path("logout/", AuthLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("api/", include(router.urls)),  # ← esto crea /api/products/, /api/categories/, etc.
]