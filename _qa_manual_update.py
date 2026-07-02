from pathlib import Path

root = Path(r'C:/proyectos_hd/proyectohd')

# Update applications/home/views.py
path = root / 'applications' / 'home' / 'views.py'
text = path.read_text(encoding='utf-8')
marker = """
    return render(request, 'home/quality_tools.html', {
        'tools': tools,
        'setup_steps': setup_steps,
        'quick_refs': quick_refs,
    })
"""
insert = """
    return render(request, 'home/quality_tools.html', {
        'tools': tools,
        'setup_steps': setup_steps,
        'quick_refs': quick_refs,
    })


@login_required(login_url='login')
def quality_tools_manual(request):
    manual_sections = [
        {
            'name': 'Playwright',
            'tag': 'E2E',
            'goal': 'Validar el login y la navegación real en navegador.',
            'steps': [
                'Instala las dependencias del proyecto.',
                'Ejecuta `playwright install` una sola vez.',
                'Levanta Django con `python manage.py runserver`.',
                'Configura las variables `PLAYWRIGHT_*`.',
                'Ejecuta `python tests/e2e/playwright_smoke.py`.',
            ],
        },
        {
            'name': 'Locust',
            'tag': 'Load',
            'goal': 'Simular usuarios concurrentes y medir rendimiento.',
            'steps': [
                'Levanta Django en local.',
                'Define `LOCUST_HOST` y credenciales de prueba.',
                'Ejecuta `locust -f locustfile.py`.',
                'Abre la interfaz web de Locust y configura usuarios.',
                'Lanza la prueba y revisa latencia, errores y throughput.',
            ],
        },
        {
            'name': 'Bandit',
            'tag': 'Security',
            'goal': 'Revisar patrones inseguros en el código Python.',
            'steps': [
                'Instala las dependencias del entorno.',
                'Ejecuta `bandit -r applications -c tools/bandit.yml`.',
                'Revisa los hallazgos por severidad.',
                'Corrige los riesgos y vuelve a ejecutar el escaneo.',
            ],
        },
        {
            'name': 'Safety',
            'tag': 'SCA',
            'goal': 'Detectar vulnerabilidades conocidas en dependencias.',
            'steps': [
                'Asegúrate de tener el entorno virtual activo.',
                'Ejecuta `safety scan --target .`.',
                'Revisa los paquetes marcados como vulnerables.',
                'Actualiza dependencias y repite la validación.',
            ],
        },
        {
            'name': 'Semgrep',
            'tag': 'SAST',
            'goal': 'Aplicar reglas semánticas para encontrar patrones peligrosos.',
            'steps': [
                'Confirma que existe `tools/semgrep.yml`.',
                'Ejecuta `semgrep scan --config tools/semgrep.yml applications`.',
                'Agrega reglas nuevas si quieres ampliar cobertura.',
                'Integra el comando en CI/CD cuando esté estable.',
            ],
        },
        {
            'name': 'pylint',
            'tag': 'Lint',
            'goal': 'Evaluar estilo, consistencia y calidad del código Python.',
            'steps': [
                'Revisa `tools/pylintrc` si necesitas ajustar reglas.',
                'Ejecuta `pylint --rcfile=tools/pylintrc --recursive=y applications`.',
                'Corrige warnings de estilo, diseño y posibles errores.',
                'Repite hasta dejar el reporte limpio o aceptable.',
            ],
        },
    ]
    return render(request, 'home/quality_tools_manual.html', {
        'manual_sections': manual_sections,
    })
"""
if marker not in text:
    raise SystemExit('quality_tools return block not found')
text = text.replace(marker, insert, 1)
path.write_text(text, encoding='utf-8')

# Update applications/home/urls.py
path = root / 'applications' / 'home' / 'urls.py'
text = path.read_text(encoding='utf-8')
needle = "    path('calidad/', profile_required('developer')(views.quality_tools), name='quality_tools'),\n"
replacement = needle + "    path('calidad/manual/', profile_required('developer')(views.quality_tools_manual), name='quality_tools_manual'),\n"
if needle not in text:
    raise SystemExit('quality_tools url not found')
text = text.replace(needle, replacement, 1)
path.write_text(text, encoding='utf-8')

# Update templates/home/quality_tools.html
path = root / 'templates' / 'home' / 'quality_tools.html'
text = path.read_text(encoding='utf-8')
old = """    <div>
        <a class="btn btn-primary" href="/">Volver al panel</a>
    </div>
</div>
"""
new = """    <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end;">
        <a class="btn btn-primary" href="/">Volver al panel</a>
        <a class="btn btn-secondary" href="/calidad/manual/">Abrir manual</a>
    </div>
</div>
"""
if old not in text:
    raise SystemExit('quality_tools hero block not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

# Create manual template
manual = """{% extends 'base.html' %}

{% block title %}Manual de herramientas de calidad{% endblock %}

{% block content %}
<div class="card page-hero">
    <div>
        <p class="eyebrow">Manual</p>
        <h2 class="hero-title">Guía para ejecutar las herramientas</h2>
        <p class="muted">Pasos concretos para correr Playwright, Locust, Bandit, Safety, Semgrep y pylint desde este proyecto.</p>
    </div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end;">
        <a class="btn btn-primary" href="/calidad/">Volver a calidad</a>
        <a class="btn btn-secondary" href="/">Volver al panel</a>
    </div>
</div>

<div class="section-grid">
    {% for section in manual_sections %}
        <div class="card">
            <div class="toolbar" style="margin-top:0;">
                <div>
                    <p class="eyebrow">{{ section.tag }}</p>
                    <h3 style="margin:0;">{{ section.name }}</h3>
                </div>
                <span class="pill">Paso a paso</span>
            </div>
            <p class="muted">{{ section.goal }}</p>
            <ol>
                {% for step in section.steps %}
                    <li>{{ step }}</li>
                {% endfor %}
            </ol>
        </div>
    {% endfor %}
</div>

<div class="card">
    <p class="eyebrow">Resumen rápido</p>
    <h3 style="margin-top:0;">Comandos principales</h3>
    <div class="section-grid">
        <div class="detail-item"><span>Playwright</span><strong><code>python tests/e2e/playwright_smoke.py</code></strong></div>
        <div class="detail-item"><span>Locust</span><strong><code>locust -f locustfile.py</code></strong></div>
        <div class="detail-item"><span>Bandit</span><strong><code>bandit -r applications -c tools/bandit.yml</code></strong></div>
        <div class="detail-item"><span>Safety</span><strong><code>safety scan --target .</code></strong></div>
        <div class="detail-item"><span>Semgrep</span><strong><code>semgrep scan --config tools/semgrep.yml applications</code></strong></div>
        <div class="detail-item"><span>pylint</span><strong><code>pylint --rcfile=tools/pylintrc --recursive=y applications</code></strong></div>
    </div>
</div>
{% endblock %}
"""
(root / 'templates' / 'home' / 'quality_tools_manual.html').write_text(manual, encoding='utf-8')

# Update tests to cover the new manual page
path = root / 'applications' / 'home' / 'tests.py'
text = path.read_text(encoding='utf-8')
needle = """    def test_quality_tools_view_renders_for_developer(self):
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
"""
replacement = needle + "\n    def test_quality_tools_manual_renders_for_developer(self):\n        self.client.force_login(self.user)\n        session = self.client.session\n        session['user_profile'] = 'developer'\n        session.save()\n\n        response = self.client.get(reverse('quality_tools_manual'))\n\n        self.assertEqual(response.status_code, 200)\n        self.assertContains(response, 'Guía para ejecutar las herramientas')\n        self.assertContains(response, 'Playwright')\n        self.assertContains(response, 'Semgrep')\n        self.assertContains(response, 'pylint')\n"
if needle not in text:
    raise SystemExit('quality_tools test not found')
text = text.replace(needle, replacement, 1)
path.write_text(text, encoding='utf-8')
