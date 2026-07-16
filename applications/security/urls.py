from django.urls import path

from applications.home.role_utils import profile_required

from . import views

app_name = "security"

urlpatterns = [

    # Dashboard principal
    path(
        "",
        profile_required("security")(views.dashboard),
        name="dashboard"
    ),

    path(
        "estado/",
        profile_required("security")(views.status_overview),
        name="status_overview"
    ),
    # Ejecutar una herramienta
    path(
        "run/<str:tool>/",
        profile_required("security")(views.run_tool),
        name="run_tool"
    ),

]