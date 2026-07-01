import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectohd.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from applications.home.models import PriorityActivity
from django.conf import settings
settings.ALLOWED_HOSTS = ['testserver', 'localhost']

u = get_user_model().objects.create_user(username='debuguser', password='12345678')
a = PriorityActivity.objects.create(title='t', priority='high', status='pending')
c = Client()
c.force_login(u)
r = c.post(reverse('priority_activity_status_update', args=[a.pk]), {'status': 'in_progress'}, content_type='application/x-www-form-urlencoded')
print('status', r.status_code)
print('content', r.content.decode())
a.refresh_from_db()
print('db', a.status)
