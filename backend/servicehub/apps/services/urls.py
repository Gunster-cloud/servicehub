from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ServiceCategoryViewSet, ServiceOrderViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'categories', ServiceCategoryViewSet)
router.register(r'orders', ServiceOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

