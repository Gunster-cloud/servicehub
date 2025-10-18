from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesMetricsViewSet, DailyActivityViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'metrics', SalesMetricsViewSet)
router.register(r'activities', DailyActivityViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

