# Proyecto HD

Sistema web desarrollado en Django para el seguimiento de producciÃ³n, tareas, rendimiento de desarrolladores y observaciones de operaciÃ³n en proyectos de software.

## CaracterÃ­sticas

- Dashboard ejecutivo con resumen de proyectos, tareas y seguimiento.
- GestiÃ³n de proyectos, tareas y seguimientos.
- Registro de rendimiento por desarrollador y semana.
- Seguimiento de productividad con filtros por usuario y semana.
- Observaciones y novedades por desarrollador.
- AutenticaciÃ³n de usuarios.

## Requisitos

- Python 3.11+
- MySQL o MariaDB
- pip

## InstalaciÃ³n

1. Clona el repositorio.
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   En Windows:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las variables de entorno en el archivo `.env`.
5. Crea la base de datos en MySQL y ajusta los valores de conexiÃ³n.
6. Ejecuta las migraciones:
   ```bash
   python manage.py migrate
   ```
7. Crea un usuario administrador:
   ```bash
   python manage.py createsuperuser
   ```
8. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```

## Estructura del proyecto

- `applications/home/` â€” lÃ³gica principal de la app.
- `templates/` â€” plantillas HTML del sistema.
- `proyectohd/` â€” configuraciÃ³n del proyecto Django.

## Uso

- Accede a la app en `http://127.0.0.1:8000/`
- Accede al panel de administraciÃ³n en `http://127.0.0.1:8000/admin/`

## Pruebas

Ejecuta:

```bash
python manage.py test
```

## Herramientas de calidad

El proyecto incluye una base para validación con:

- Playwright para pruebas end-to-end.
- Locust para pruebas de carga.
- Bandit para análisis de seguridad.
- Safety para análisis de vulnerabilidades en dependencias.
- Semgrep para reglas SAST personalizadas.
- pylint para linting y calidad de código.

### Instalar navegadores de Playwright

```bash
playwright install
```

### Ejecutar Playwright

```powershell
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:8000'
$env:PLAYWRIGHT_DEV_USER='tu_usuario'
$env:PLAYWRIGHT_DEV_PASSWORD='tu_password'
$env:PLAYWRIGHT_TEST_USER='tu_usuario_tester'
$env:PLAYWRIGHT_TEST_PASSWORD='tu_password_tester'
python tests/e2e/playwright_smoke.py
```

### Ejecutar Locust

```powershell
$env:LOCUST_HOST='http://127.0.0.1:8000'
$env:LOCUST_DEV_USER='tu_usuario'
$env:LOCUST_DEV_PASSWORD='tu_password'
$env:LOCUST_TEST_USER='tu_usuario_tester'
$env:LOCUST_TEST_PASSWORD='tu_password_tester'
locust -f locustfile.py
```

### Ejecutar Bandit

```powershell
bandit -r applications -c tools/bandit.yml
```

### Ejecutar Safety

```powershell
safety scan --target .
```

### Ejecutar Semgrep

```powershell
semgrep scan --config tools/semgrep.yml applications
```

### Ejecutar pylint

```powershell
pylint --rcfile=tools/pylintrc --recursive=y applications
```

### Probar Selenium

```powershell
python manage.py test applications.home.tests.LoginSeleniumTest
```

