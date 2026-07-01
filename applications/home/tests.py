from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FollowUp, PriorityActivity, Project, Status, Task


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

    def test_priority_activity_update_view_renders(self):
        activity = PriorityActivity.objects.create(title='Validar entorno', priority='critical', status='pending')
        self.client.force_login(self.user)
        response = self.client.get(reverse('priority_activity_update', args=[activity.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar actividad')

    def test_priority_activities_filter_and_kanban_render(self):
        PriorityActivity.objects.create(title='Validar entorno', priority='critical', status='pending')
        PriorityActivity.objects.create(title='Revisar seguridad', priority='high', status='done')
        self.client.force_login(self.user)
        response = self.client.get(reverse('priority_activities'), {'priority': 'critical', 'status': 'pending'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tablero kanban')
        self.assertContains(response, 'Validar entorno')
        self.assertNotContains(response, 'Revisar seguridad')

    def test_priority_activity_status_update(self):
        activity = PriorityActivity.objects.create(title='Actualizar entorno', priority='high', status='pending')
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('priority_activity_status_update', args=[activity.pk]),
            data={'status': 'in_progress'},
            content_type='application/x-www-form-urlencoded',
        )

        self.assertEqual(response.status_code, 200)
        activity.refresh_from_db()
        self.assertEqual(activity.status, 'in_progress')
