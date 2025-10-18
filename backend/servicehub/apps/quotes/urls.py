from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuoteViewSet, ProposalViewSet

router = DefaultRouter()
router.register(r'quotes', QuoteViewSet)
router.register(r'proposals', ProposalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

