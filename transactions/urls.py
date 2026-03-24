from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClientViewSet, ProductViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"products", ProductViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
