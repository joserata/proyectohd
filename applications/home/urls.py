from django.urls import path

from applications.home.role_utils import profile_required

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', profile_required('developer')(views.dashboard), name='dashboard'),
    path('usuarios/', profile_required('developer')(views.user_list), name='user_list'),
    path('estados/', profile_required('developer')(views.create_status), name='create_status'),
    path('productividad/', profile_required('developer')(views.productivity_dashboard), name='productivity_dashboard'),
    path('productividad/registrar/', profile_required('developer')(views.register_performance), name='register_performance'),
    path('observaciones/nueva/', profile_required('developer')(views.create_observation), name='create_observation'),
    path('actividades-prioritarias/', profile_required('developer')(views.priority_activities), name='priority_activities'),
    path('actividades-prioritarias/<int:pk>/editar/', profile_required('developer')(views.priority_activity_update), name='priority_activity_update'),
    path('actividades-prioritarias/<int:pk>/eliminar/', profile_required('developer')(views.priority_activity_delete), name='priority_activity_delete'),
    path('actividades-prioritarias/<int:pk>/estado/', profile_required('developer')(views.priority_activity_status_update), name='priority_activity_status_update'),
    path('proyectos/', profile_required('developer')(views.ProjectListView.as_view()), name='project_list'),
    path('proyectos/nuevo/', profile_required('developer')(views.ProjectCreateView.as_view()), name='project_create'),
    path('proyectos/<int:pk>/editar/', profile_required('developer')(views.ProjectUpdateView.as_view()), name='project_update'),
    path('proyectos/<int:pk>/eliminar/', profile_required('developer')(views.ProjectDeleteView.as_view()), name='project_delete'),
    path('tareas/', profile_required('developer')(views.TaskListView.as_view()), name='task_list'),
    path('tareas/nuevo/', profile_required('developer')(views.TaskCreateView.as_view()), name='task_create'),
    path('tareas/<int:pk>/editar/', profile_required('developer')(views.TaskUpdateView.as_view()), name='task_update'),
    path('tareas/<int:pk>/eliminar/', profile_required('developer')(views.TaskDeleteView.as_view()), name='task_delete'),
    path('seguimientos/', profile_required('developer')(views.FollowUpListView.as_view()), name='followup_list'),
    path('seguimientos/nuevo/', profile_required('developer')(views.FollowUpCreateView.as_view()), name='followup_create'),
    path('seguimientos/<int:pk>/editar/', profile_required('developer')(views.FollowUpUpdateView.as_view()), name='followup_update'),
    path('seguimientos/<int:pk>/eliminar/', profile_required('developer')(views.FollowUpDeleteView.as_view()), name='followup_delete'),
    path('calidad/', profile_required('developer')(views.quality_tools), name='quality_tools'),
    path('calidad/manual/', profile_required('tester')(views.quality_tools_manual), name='quality_tools_manual'),
]
