from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('usuarios/', views.user_list, name='user_list'),
    path('estados/', views.create_status, name='create_status'),
    path('productividad/', views.productivity_dashboard, name='productivity_dashboard'),
    path('productividad/registrar/', views.register_performance, name='register_performance'),
    path('observaciones/nueva/', views.create_observation, name='create_observation'),
    path('actividades-prioritarias/', views.priority_activities, name='priority_activities'),
    path('actividades-prioritarias/<int:pk>/editar/', views.priority_activity_update, name='priority_activity_update'),
    path('actividades-prioritarias/<int:pk>/eliminar/', views.priority_activity_delete, name='priority_activity_delete'),
    path('actividades-prioritarias/<int:pk>/estado/', views.priority_activity_status_update, name='priority_activity_status_update'),
    path('proyectos/', views.ProjectListView.as_view(), name='project_list'),
    path('proyectos/nuevo/', views.ProjectCreateView.as_view(), name='project_create'),
    path('proyectos/<int:pk>/editar/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('proyectos/<int:pk>/eliminar/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('tareas/', views.TaskListView.as_view(), name='task_list'),
    path('tareas/nuevo/', views.TaskCreateView.as_view(), name='task_create'),
    path('tareas/<int:pk>/editar/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tareas/<int:pk>/eliminar/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('seguimientos/', views.FollowUpListView.as_view(), name='followup_list'),
    path('seguimientos/nuevo/', views.FollowUpCreateView.as_view(), name='followup_create'),
    path('seguimientos/<int:pk>/editar/', views.FollowUpUpdateView.as_view(), name='followup_update'),
    path('seguimientos/<int:pk>/eliminar/', views.FollowUpDeleteView.as_view(), name='followup_delete'),
]
