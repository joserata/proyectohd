from unittest import SkipTest, skipUnless

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.urls import reverse

from .models import FollowUp, PriorityActivity, Project, Status, Task

try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.support.ui import Select
except ImportError:  # pragma: no cover - optional dependency
    webdriver = None
    WebDriverException = Exception
    By = None
    Select = None
    ChromeOptions = None
    FirefoxOptions = None


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

    def test_quality_tools_view_renders_for_developer(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['user_profile'] = 'developer'
        session.save()

        response = self.client.get(reverse('quality_tools'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Playwright')
        self.assertContains(response, 'Locust')
        self.assertContains(response, 'Bandit')
        self.assertContains(response, 'Safety')
        self.assertContains(response, 'Semgrep')
        self.assertContains(response, 'pylint')

    def test_quality_tools_manual_renders_for_developer(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['user_profile'] = 'developer'
        session.save()

        response = self.client.get(reverse('quality_tools_manual'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guía para ejecutar las herramientas')
        self.assertContains(response, 'Instalar')
        self.assertContains(response, 'Ejecutar')
        self.assertContains(response, 'Interpretar resultado')
        self.assertContains(response, 'Playwright')
        self.assertContains(response, 'Semgrep')
        self.assertContains(response, 'pylint')

    def test_quality_tools_manual_renders_for_tester(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['user_profile'] = 'tester'
        session.save()

        response = self.client.get(reverse('quality_tools_manual'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Guía para ejecutar las herramientas')
        self.assertContains(response, 'Playwright')
        self.assertContains(response, 'Semgrep')
        self.assertContains(response, 'pylint')

    def test_login_redirects_security_profile_to_security_dashboard(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': self.user.username,
                'password': '12345678',
                'profile': 'security',
            },
        )

        self.assertRedirects(response, reverse('security:dashboard'))

        dashboard_response = self.client.get(reverse('security:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertTemplateUsed(dashboard_response, 'security/dashboard.html')


@skipUnless(webdriver is not None, 'Selenium no está instalado')
class LoginSeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = cls._build_driver()

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'driver', None):
            cls.driver.quit()
        super().tearDownClass()

    @classmethod
    def _build_driver(cls):
        errors = []

        if ChromeOptions is not None:
            try:
                options = ChromeOptions()
                options.add_argument('--headless=new')
                options.add_argument('--window-size=1440,1200')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                return webdriver.Chrome(options=options)
            except WebDriverException as exc:
                errors.append(f'Chrome: {exc}')

        if FirefoxOptions is not None:
            try:
                options = FirefoxOptions()
                options.add_argument('-headless')
                return webdriver.Firefox(options=options)
            except WebDriverException as exc:
                errors.append(f'Firefox: {exc}')

        raise SkipTest('No se pudo iniciar un navegador para Selenium: ' + ' | '.join(errors))

    def setUp(self):
        self.User = get_user_model()
        self.dev_user = self.User.objects.create_user(username='dev.selenium', password='12345678')
        self.test_user = self.User.objects.create_user(username='qa.selenium', password='12345678')

    def test_login_selector_and_role_routing(self):
        self.driver.get(f'{self.live_server_url}{reverse("login")}')
        profile_select = Select(self.driver.find_element(By.NAME, 'profile'))
        options = [option.text for option in profile_select.options]
        self.assertIn('Desarrollo', options)
        self.assertIn('Tester', options)

        self.driver.find_element(By.NAME, 'username').send_keys(self.dev_user.username)
        self.driver.find_element(By.NAME, 'password').send_keys('12345678')
        profile_select.select_by_visible_text('Desarrollo')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertIn(reverse('dashboard'), self.driver.current_url)

        self.driver.get(f'{self.live_server_url}{reverse("login")}')
        self.driver.find_element(By.NAME, 'username').send_keys(self.test_user.username)
        self.driver.find_element(By.NAME, 'password').send_keys('12345678')
        Select(self.driver.find_element(By.NAME, 'profile')).select_by_visible_text('Tester')
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self.assertIn(reverse('pruebastest_index'), self.driver.current_url)

