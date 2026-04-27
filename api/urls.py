from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TutorViewSet, MateriaViewSet, TutoriaViewSet,
    DisponibilidadViewSet, ResenaViewSet, UserAdminViewSet,
    AuthViewSet
)

router = DefaultRouter()
router.register(r'tutores', TutorViewSet)
router.register(r'materias', MateriaViewSet)
router.register(r'tutorias', TutoriaViewSet)
router.register(r'disponibilidades', DisponibilidadViewSet)
router.register(r'resenas', ResenaViewSet)
router.register(r'usuarios', UserAdminViewSet, basename='usuarios')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]