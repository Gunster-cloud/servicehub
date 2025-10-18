from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientContactViewSet

router = DefaultRouter()
router.register(r'', ClientViewSet)
router.register(r'contacts', ClientContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

