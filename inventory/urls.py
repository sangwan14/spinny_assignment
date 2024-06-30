from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CuboidViewSet

router = DefaultRouter()
router.register(r'cuboids', CuboidViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

