from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Materia, Tutor, Tutoria

class MateriaAPITestCase(APITestCase):
    def setUp(self):
        self.materia_data = {'nombre': 'Matemáticas', 'descripcion': 'Curso de matemáticas básicas'}
        self.url = reverse('materia-list')

    def test_create_materia(self):
        response = self.client.post(self.url, self.materia_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Materia.objects.count(), 1)
        self.assertEqual(Materia.objects.get().nombre, 'Matemáticas')

    def test_get_materias(self):
        Materia.objects.create(**self.materia_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class TutorAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tutor1', password='pass123')
        self.materia = Materia.objects.create(nombre='Física')
        self.tutor_data = {
            'usuario_id': self.user.id,
            'especialidad': 'Física Cuántica',
            'materias_ids': [self.materia.id],
            'nivel_experiencia': 'experto',
            'tarifa_por_hora': 50.00
        }
        self.url = reverse('tutor-list')

    def test_create_tutor(self):
        response = self.client.post(self.url, self.tutor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tutor.objects.count(), 1)

    def test_get_tutores(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
