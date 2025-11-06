# tienda/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Intentamos importar las vistas como CLASES (CBV).
# Si no existen, caemos a funciones (FBV) sin reventar el proyecto.
use_cbv = True
try:
    from .views import (
        HomeView, AuthLoginView, AuthLogoutView, SignUpView,
        ContactView, SalesView,
        ProductViewSet, CategoryViewSet, SaleViewSet, SaleItemViewSet,
    )
except Exception:
    use_cbv = False
    from . import views  # funciones
    # Aún así esperamos que los ViewSets existan en views
    ProductViewSet = getattr(views, "ProductViewSet")
    CategoryViewSet = getattr(views, "CategoryViewSet")
    SaleViewSet = getattr(views, "SaleViewSet")
    SaleItemViewSet = getattr(views, "SaleItemViewSet")

app_name = "tienda"

# Router API (DRF)
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"sale-items", SaleItemViewSet, basename="sale-item")

urlpatterns = [
    # Endpoints API (browsable API incluida para login en panel DRF)
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]

if use_cbv:
    # Vistas como clases
    urlpatterns += [
        path("", HomeView.as_view(), name="home"),
        path("login/", AuthLoginView.as_view(), name="login"),
        path("logout/", AuthLogoutView.as_view(), name="logout"),
        path("signup/", SignUpView.as_view(), name="signup"),
        path("contacto/", ContactView.as_view(), name="contacto"),
        path("ventas/", SalesView.as_view(), name="ventas"),
    ]
else:
    # Vistas como funciones
    urlpatterns += [
        path("", views.home, name="home"),
        path("login/", views.login_view, name="login"),
        path("logout/", views.logout_view, name="logout"),
        path("signup/", views.signup_view, name="signup"),
        path("contacto/", views.contacto, name="contacto"),
        path("ventas/", views.ventas, name="ventas"),
    ]
