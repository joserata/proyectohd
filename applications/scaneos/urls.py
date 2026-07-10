from django.urls import path

from . import views


app_name = "scaneos"


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "run/",
        views.run_scan,
        name="run_scan",
    ),

    path(
        "history/",
        views.history,
        name="history",
    ),

    path(
        "detail/<int:pk>/",
        views.detail,
        name="detail",
    ),

    path(
        "tools/",
        views.available_tools,
        name="available_tools",
    ),

]