from django.urls import path

from . import views

app_name = "security"

urlpatterns = [

    # Dashboard principal
    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    # Ejecutar una herramienta
    path(
        "run/<str:tool>/",
        views.run_tool,
        name="run_tool"
    ),

]