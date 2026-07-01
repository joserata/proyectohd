from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FollowUp, Project, Status, Task


class GestionSoftwareModelsTest(TestCase):
    def setUp(self):
        self.status = Status.objects.create(name='En progreso', category='task')
        self.project = Project.objects.create(name='Portal interno', description='Gestión de desarrollo', status=self.status)
        self.user = get_user_model().objects.create_user(username='dev1', password='12345678')

    def test_crear_tarea_y_seguimiento(self):
        task = Task.objects.create(
            title='Implementar login',
            description='Crear autenticación',
            project=self.project,
            status=self.status,
            assigned_to=self.user,
        )
        follow_up = FollowUp.objects.create(task=task, comment='Se revisó el avance', created_by=self.user)

        self.assertEqual(task.project.name, 'Portal interno')
        self.assertEqual(follow_up.task.title, 'Implementar login')
        self.assertEqual(task.assigned_to.username, 'dev1')

    def test_dashboard_view_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tablero ejecutivo de desarrollo')
        self.assertContains(response, 'Flujo de desarrollo a producción')
        self.assertContains(response, 'Análisis')
        self.assertContains(response, 'QA')

    def test_productivity_dashboard_renders_dynamic_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('productivity_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resumen dinámico por producción y rendimiento')
        self.assertContains(response, 'Perfil de desarrollador')
