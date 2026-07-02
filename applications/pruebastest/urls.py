from django.urls import path

from applications.home.role_utils import profile_required

from . import views

urlpatterns = [
    path('', profile_required('tester')(views.index), name='pruebastest_index'),
    path('proyectos/', profile_required('tester')(views.proyecto_list), name='pruebastest_proyectos'),
    path('proyectos/nuevo/', profile_required('tester')(views.proyecto_create), name='pruebastest_proyecto_create'),
    path('proyectos/<int:pk>/', profile_required('tester')(views.proyecto_detail), name='pruebastest_proyecto_detail'),
    path('proyectos/<int:pk>/editar/', profile_required('tester')(views.proyecto_update), name='pruebastest_proyecto_update'),
    path('proyectos/<int:pk>/eliminar/', profile_required('tester')(views.proyecto_delete), name='pruebastest_proyecto_delete'),
    path('modulos/', profile_required('tester')(views.modulo_list), name='pruebastest_modulos'),
    path('modulos/nuevo/', profile_required('tester')(views.modulo_create), name='pruebastest_modulo_create'),
    path('modulos/<int:pk>/', profile_required('tester')(views.modulo_detail), name='pruebastest_modulo_detail'),
    path('modulos/<int:pk>/editar/', profile_required('tester')(views.modulo_update), name='pruebastest_modulo_update'),
    path('modulos/<int:pk>/eliminar/', profile_required('tester')(views.modulo_delete), name='pruebastest_modulo_delete'),
    path('requerimientos/', profile_required('tester')(views.requerimiento_list), name='pruebastest_requerimientos'),
    path('requerimientos/nuevo/', profile_required('tester')(views.requerimiento_create), name='pruebastest_requerimiento_create'),
    path('requerimientos/<int:pk>/', profile_required('tester')(views.requerimiento_detail), name='pruebastest_requerimiento_detail'),
    path('requerimientos/<int:pk>/editar/', profile_required('tester')(views.requerimiento_update), name='pruebastest_requerimiento_update'),
    path('requerimientos/<int:pk>/eliminar/', profile_required('tester')(views.requerimiento_delete), name='pruebastest_requerimiento_delete'),
    path('casos/', profile_required('tester')(views.caso_list), name='pruebastest_casos'),
    path('casos/nuevo/', profile_required('tester')(views.caso_create), name='pruebastest_caso_create'),
    path('casos/<int:pk>/', profile_required('tester')(views.caso_detail), name='pruebastest_caso_detail'),
    path('casos/<int:pk>/editar/', profile_required('tester')(views.caso_update), name='pruebastest_caso_update'),
    path('casos/<int:pk>/eliminar/', profile_required('tester')(views.caso_delete), name='pruebastest_caso_delete'),
    path('planes/', profile_required('tester')(views.plan_list), name='pruebastest_planes'),
    path('planes/nuevo/', profile_required('tester')(views.plan_create), name='pruebastest_plan_create'),
    path('planes/<int:pk>/', profile_required('tester')(views.plan_detail), name='pruebastest_plan_detail'),
    path('planes/<int:pk>/editar/', profile_required('tester')(views.plan_update), name='pruebastest_plan_update'),
    path('planes/<int:pk>/eliminar/', profile_required('tester')(views.plan_delete), name='pruebastest_plan_delete'),
    path('ejecuciones/', profile_required('tester')(views.ejecucion_list), name='pruebastest_ejecuciones'),
    path('ejecuciones/nuevo/', profile_required('tester')(views.ejecucion_create), name='pruebastest_ejecucion_create'),
    path('ejecuciones/<int:pk>/', profile_required('tester')(views.ejecucion_detail), name='pruebastest_ejecucion_detail'),
    path('ejecuciones/<int:pk>/editar/', profile_required('tester')(views.ejecucion_update), name='pruebastest_ejecucion_update'),
    path('ejecuciones/<int:pk>/eliminar/', profile_required('tester')(views.ejecucion_delete), name='pruebastest_ejecucion_delete'),
    path('bugs/', profile_required('tester')(views.bug_list), name='pruebastest_bugs'),
    path('bugs/nuevo/', profile_required('tester')(views.bug_create), name='pruebastest_bug_create'),
    path('bugs/<int:pk>/', profile_required('tester')(views.bug_detail), name='pruebastest_bug_detail'),
    path('bugs/<int:pk>/editar/', profile_required('tester')(views.bug_update), name='pruebastest_bug_update'),
    path('bugs/<int:pk>/eliminar/', profile_required('tester')(views.bug_delete), name='pruebastest_bug_delete'),
]
