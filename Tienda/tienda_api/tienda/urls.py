from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomeView, AuthLoginView, AuthLogoutView, SignUpView,
    ProductViewSet, CategoryViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", AuthLoginView.as_view(), name="login"),
    path("logout/", AuthLogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("api/", include(router.urls)),   # ← esto crea /api/products/ y /api/categories/
]

