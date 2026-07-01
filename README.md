# Proyecto HD

Sistema web desarrollado en Django para el seguimiento de producción, tareas, rendimiento de desarrolladores y observaciones de operación en proyectos de software.

## Características

- Dashboard ejecutivo con resumen de proyectos, tareas y seguimiento.
- Gestión de proyectos, tareas y seguimientos.
- Registro de rendimiento por desarrollador y semana.
- Seguimiento de productividad con filtros por usuario y semana.
- Observaciones y novedades por desarrollador.
- Autenticación de usuarios.

## Requisitos

- Python 3.11+
- MySQL o MariaDB
- pip

## Instalación

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
5. Crea la base de datos en MySQL y ajusta los valores de conexión.
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

- `applications/home/` — lógica principal de la app.
- `templates/` — plantillas HTML del sistema.
- `proyectohd/` — configuración del proyecto Django.

## Uso

- Accede a la app en `http://127.0.0.1:8000/`
- Accede al panel de administración en `http://127.0.0.1:8000/admin/`

## Pruebas

Ejecuta:

```bash
python manage.py test
```
