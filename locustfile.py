import os

from locust import HttpUser, SequentialTaskSet, between, task


class BaseLoginFlow(SequentialTaskSet):
    profile = 'developer'
    username = ''
    password = ''
    landing_path = '/'
    extra_paths = ()

    def on_start(self):
        self._login()

    def _login(self):
        response = self.client.get('/login/')
        csrf = response.cookies.get('csrftoken')
        headers = {'X-CSRFToken': csrf.value if csrf else ''}
        self.client.post('/login/', data={
            'username': self.username,
            'password': self.password,
            'profile': self.profile,
        }, headers=headers, name='login', allow_redirects=True)

    @task
    def landing(self):
        self.client.get(self.landing_path, name=self.landing_path)

    @task(3)
    def extras(self):
        for path in self.extra_paths:
            self.client.get(path, name=path)


class DeveloperFlow(BaseLoginFlow):
    profile = 'developer'
    username = os.getenv('LOCUST_DEV_USER', 'dev1')
    password = os.getenv('LOCUST_DEV_PASSWORD', '12345678')
    landing_path = '/'
    extra_paths = ('/productividad/', '/proyectos/', '/tareas/', '/seguimientos/', '/calidad/')


class TesterFlow(BaseLoginFlow):
    profile = 'tester'
    username = os.getenv('LOCUST_TEST_USER', 'qa.selenium')
    password = os.getenv('LOCUST_TEST_PASSWORD', '12345678')
    landing_path = '/pruebastest/'
    extra_paths = ('/pruebastest/proyectos/', '/pruebastest/modulos/', '/pruebastest/casos/', '/pruebastest/bugs/')


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    tasks = [DeveloperFlow, TesterFlow]
    host = os.getenv('LOCUST_HOST', 'http://127.0.0.1:8000')
