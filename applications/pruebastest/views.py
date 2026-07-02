from django.db.models import Q
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from datetime import timedelta

from django.utils import timezone

from .models import (
    TestBug,
    TestCaso,
    TestEjecucion,
    TestModulo,
    TestPlan,
    TestProyecto,
    TestRequerimiento,
)


def _fmt_date(value):
    if not value:
        return '-'
    return value.strftime('%Y-%m-%d')


def _fmt_datetime(value):
    if not value:
        return '-'
    return value.strftime('%Y-%m-%d %H:%M')


def _select_options(values, include_all=True):
    options = []
    if include_all:
        options.append({'value': '', 'label': 'Todos'})
    for item in values:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            value, label = item[0], item[1]
        else:
            value, label = item, item
        if value not in (None, ''):
            options.append({'value': value, 'label': label})
    return options


def _build_actions(prefix, pk):
    return {
        'detail_url': reverse(f'pruebastest_{prefix}_detail', args=[pk]),
        'edit_url': reverse(f'pruebastest_{prefix}_update', args=[pk]),
        'delete_url': reverse(f'pruebastest_{prefix}_delete', args=[pk]),
    }


def _save_form(request, model, fields, template_title, success_name, instance=None, extra_context=None):
    form_class = modelform_factory(model, fields=fields)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            now = timezone.now()
            if instance is None and hasattr(obj, 'fecha_creacion') and not getattr(obj, 'fecha_creacion', None):
                obj.fecha_creacion = now
            if hasattr(obj, 'fecha_actualizacion'):
                obj.fecha_actualizacion = now
            obj.save()
            form.save_m2m()
            return redirect(success_name)
    else:
        form = form_class(instance=instance)

    context = {
        'title': template_title,
        'form': form,
        'cancel_url': reverse(success_name),
        'is_update': instance is not None,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, 'pruebastest/entity_form.html', context)


def _delete_entity(request, instance, title, success_name, detail_name=None):
    if request.method == 'POST':
        instance.delete()
        return redirect(success_name)
    context = {
        'title': title,
        'object': instance,
        'cancel_url': reverse(success_name),
    }
    if detail_name:
        context['detail_url'] = reverse(detail_name, args=[instance.pk])
    return render(request, 'pruebastest/entity_confirm_delete.html', context)


def _detail_entity(request, title, instance, fields, back_name, edit_name, delete_name):
    rows = []
    for label, value in fields:
        if isinstance(value, list):
            value = ', '.join(str(item) for item in value) if value else '-'
        rows.append({'label': label, 'value': value if value not in (None, '') else '-'})
    return render(request, 'pruebastest/entity_detail.html', {
        'title': title,
        'object': instance,
        'fields': rows,
        'back_url': reverse(back_name),
        'edit_url': reverse(edit_name, args=[instance.pk]),
        'delete_url': reverse(delete_name, args=[instance.pk]),
    })


def index(request):
    stats = [
        ('Proyectos', TestProyecto.objects.count()),
        ('Módulos', TestModulo.objects.count()),
        ('Requerimientos', TestRequerimiento.objects.count()),
        ('Casos', TestCaso.objects.count()),
        ('Planes', TestPlan.objects.count()),
        ('Ejecuciones', TestEjecucion.objects.count()),
        ('Bugs', TestBug.objects.count()),
    ]
    sections = [
        {'name': 'Proyectos', 'url': 'pruebastest_proyectos'},
        {'name': 'Módulos', 'url': 'pruebastest_modulos'},
        {'name': 'Requerimientos', 'url': 'pruebastest_requerimientos'},
        {'name': 'Casos', 'url': 'pruebastest_casos'},
        {'name': 'Planes', 'url': 'pruebastest_planes'},
        {'name': 'Ejecuciones', 'url': 'pruebastest_ejecuciones'},
        {'name': 'Bugs', 'url': 'pruebastest_bugs'},
    ]

    total_records = sum(value for _label, value in stats)
    recent_30_days = (
        TestProyecto.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestModulo.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestRequerimiento.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestCaso.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestPlan.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestEjecucion.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
        + TestBug.objects.filter(fecha_reporte__gte=timezone.now() - timedelta(days=30)).count()
    )
    recent_7_days = (
        TestProyecto.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestModulo.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestRequerimiento.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestCaso.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestPlan.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestEjecucion.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
        + TestBug.objects.filter(fecha_reporte__gte=timezone.now() - timedelta(days=7)).count()
    )
    bug_total = stats[-1][1]
    execution_total = stats[-2][1]
    bug_to_execution_ratio = round((bug_total / execution_total) * 100, 1) if execution_total else 0
    max_count = max((value for _label, value in stats), default=1) or 1

    chart_items = []
    palette = ['#0d3b66', '#1d72a0', '#167d82', '#17bebb', '#2a9d8f', '#4f6bed', '#7c3aed']
    for index, (label, value) in enumerate(stats):
        chart_items.append({
            'label': label,
            'value': value,
            'share': round((value / total_records) * 100, 1) if total_records else 0,
            'width': round((value / max_count) * 100, 1) if max_count else 0,
            'color': palette[index % len(palette)],
        })

    recent_items = [
        {
            'label': 'Proyecto',
            'title': item.nombre,
            'meta': f'{item.codigo} · {item.estado or "Sin estado"}',
            'time': _fmt_datetime(item.fecha_creacion),
            'url': reverse('pruebastest_proyecto_detail', args=[item.pk]),
        }
        for item in TestProyecto.objects.order_by('-fecha_creacion')[:2]
    ]
    recent_items.extend([
        {
            'label': 'Módulo',
            'title': item.nombre,
            'meta': f'{item.codigo} · {item.estado or "Sin estado"}',
            'time': _fmt_datetime(item.fecha_creacion),
            'url': reverse('pruebastest_modulo_detail', args=[item.pk]),
        }
        for item in TestModulo.objects.select_related('proyecto').order_by('-fecha_creacion')[:1]
    ])
    recent_items.extend([
        {
            'label': 'Ejecución',
            'title': f'Ejecución #{item.id}',
            'meta': f'{item.resultado or "Sin resultado"} · {item.plan_caso.plan.codigo if item.plan_caso and item.plan_caso.plan else "Plan sin código"}',
            'time': _fmt_datetime(item.fecha_creacion),
            'url': reverse('pruebastest_ejecucion_detail', args=[item.pk]),
        }
        for item in TestEjecucion.objects.select_related('plan_caso__plan', 'plan_caso__caso').order_by('-fecha_creacion')[:1]
    ])
    recent_items.extend([
        {
            'label': 'Bug',
            'title': item.titulo,
            'meta': f'{item.codigo} · {item.estado or "Sin estado"}',
            'time': _fmt_datetime(item.fecha_reporte),
            'url': reverse('pruebastest_bug_detail', args=[item.pk]),
        }
        for item in TestBug.objects.order_by('-fecha_reporte')[:2]
    ])

    context = {
        'stats': stats,
        'sections': sections,
        'chart_items': chart_items,
        'recent_items': recent_items,
        'dashboard_kpis': [
            {'label': 'Total de registros', 'value': total_records, 'hint': 'Suma de todas las entidades del módulo'},
            {'label': 'Actividad 30 días', 'value': recent_30_days, 'hint': 'Movimientos recientes en creación y reporte'},
            {'label': 'Actividad 7 días', 'value': recent_7_days, 'hint': 'Último pulso operativo'},
            {'label': 'Bugs / ejecuciones', 'value': f'{bug_to_execution_ratio}%', 'hint': 'Incidencia relativa sobre ejecuciones'},
        ],
    }
    return render(request, 'pruebastest/index.html', context)


def proyecto_list(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    proyectos_qs = TestProyecto.objects.all().order_by('-fecha_creacion')
    if q:
        proyectos_qs = proyectos_qs.filter(
            Q(codigo__icontains=q)
            | Q(nombre__icontains=q)
            | Q(cliente__icontains=q)
            | Q(estado__icontains=q)
        )
    if estado:
        proyectos_qs = proyectos_qs.filter(estado=estado)

    rows = []
    for proyecto in proyectos_qs[:50]:
        rows.append({
            'values': [
                proyecto.codigo,
                proyecto.nombre,
                proyecto.estado or '-',
                proyecto.cliente or '-',
                _fmt_datetime(proyecto.fecha_creacion),
            ],
            'actions': _build_actions('proyecto', proyecto.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código, nombre o cliente'},
        {'type': 'select', 'name': 'estado', 'label': 'Estado', 'value': estado, 'options': _select_options(TestProyecto.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct().order_by('estado'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Proyectos',
        'headers': ['Código', 'Nombre', 'Estado', 'Cliente', 'Creación'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_proyecto_create'),
        'back_url': reverse('pruebastest_index'),
    })


def proyecto_detail(request, pk):
    proyecto = get_object_or_404(TestProyecto, pk=pk)
    return _detail_entity(request, 'Proyecto', proyecto, [
        ('Código', proyecto.codigo),
        ('Nombre', proyecto.nombre),
        ('Descripción', proyecto.descripcion),
        ('Cliente', proyecto.cliente),
        ('Versión actual', proyecto.version_actual),
        ('Estado', proyecto.estado),
        ('Fecha inicio', _fmt_date(proyecto.fecha_inicio)),
        ('Fecha fin', _fmt_date(proyecto.fecha_fin)),
        ('Creado por', proyecto.creado_por),
        ('Fecha creación', _fmt_datetime(proyecto.fecha_creacion)),
        ('Fecha actualización', _fmt_datetime(proyecto.fecha_actualizacion)),
    ], 'pruebastest_proyectos', 'pruebastest_proyecto_update', 'pruebastest_proyecto_delete')


def proyecto_create(request):
    return _save_form(
        request,
        TestProyecto,
        ['codigo', 'nombre', 'descripcion', 'cliente', 'version_actual', 'estado', 'fecha_inicio', 'fecha_fin', 'creado_por'],
        'Nuevo proyecto',
        'pruebastest_proyectos',
    )


def proyecto_update(request, pk):
    proyecto = get_object_or_404(TestProyecto, pk=pk)
    return _save_form(
        request,
        TestProyecto,
        ['codigo', 'nombre', 'descripcion', 'cliente', 'version_actual', 'estado', 'fecha_inicio', 'fecha_fin', 'creado_por'],
        'Editar proyecto',
        'pruebastest_proyectos',
        instance=proyecto,
    )


def proyecto_delete(request, pk):
    proyecto = get_object_or_404(TestProyecto, pk=pk)
    return _delete_entity(request, proyecto, 'Eliminar proyecto', 'pruebastest_proyectos')


def modulo_list(request):
    q = request.GET.get('q', '').strip()
    proyecto_id = request.GET.get('proyecto', '').strip()
    estado = request.GET.get('estado', '').strip()
    modulos_qs = TestModulo.objects.select_related('proyecto').order_by('-fecha_creacion')
    if q:
        modulos_qs = modulos_qs.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if proyecto_id:
        modulos_qs = modulos_qs.filter(proyecto_id=proyecto_id)
    if estado:
        modulos_qs = modulos_qs.filter(estado=estado)

    rows = []
    for modulo in modulos_qs[:50]:
        rows.append({
            'values': [
                modulo.codigo,
                modulo.nombre,
                modulo.proyecto.codigo if modulo.proyecto else '-',
                modulo.estado or '-',
                _fmt_datetime(modulo.fecha_creacion),
            ],
            'actions': _build_actions('modulo', modulo.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código o nombre'},
        {'type': 'select', 'name': 'proyecto', 'label': 'Proyecto', 'value': proyecto_id, 'options': _select_options(TestProyecto.objects.order_by('codigo').values_list('id', 'codigo'))},
        {'type': 'select', 'name': 'estado', 'label': 'Estado', 'value': estado, 'options': _select_options(TestModulo.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct().order_by('estado'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Módulos',
        'headers': ['Código', 'Nombre', 'Proyecto', 'Estado', 'Creación'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_modulo_create'),
        'back_url': reverse('pruebastest_index'),
    })


def modulo_detail(request, pk):
    modulo = get_object_or_404(TestModulo, pk=pk)
    return _detail_entity(request, 'Módulo', modulo, [
        ('Proyecto', modulo.proyecto),
        ('Código', modulo.codigo),
        ('Nombre', modulo.nombre),
        ('Descripción', modulo.descripcion),
        ('Prioridad', modulo.prioridad),
        ('Estado', modulo.estado),
        ('Fecha creación', _fmt_datetime(modulo.fecha_creacion)),
    ], 'pruebastest_modulos', 'pruebastest_modulo_update', 'pruebastest_modulo_delete')


def modulo_create(request):
    return _save_form(
        request,
        TestModulo,
        ['proyecto', 'codigo', 'nombre', 'descripcion', 'prioridad', 'estado'],
        'Nuevo módulo',
        'pruebastest_modulos',
    )


def modulo_update(request, pk):
    modulo = get_object_or_404(TestModulo, pk=pk)
    return _save_form(
        request,
        TestModulo,
        ['proyecto', 'codigo', 'nombre', 'descripcion', 'prioridad', 'estado'],
        'Editar módulo',
        'pruebastest_modulos',
        instance=modulo,
    )


def modulo_delete(request, pk):
    modulo = get_object_or_404(TestModulo, pk=pk)
    return _delete_entity(request, modulo, 'Eliminar módulo', 'pruebastest_modulos')


def requerimiento_list(request):
    q = request.GET.get('q', '').strip()
    modulo_id = request.GET.get('modulo', '').strip()
    prioridad = request.GET.get('prioridad', '').strip()
    requerimientos_qs = TestRequerimiento.objects.select_related('modulo').order_by('-fecha_creacion')
    if q:
        requerimientos_qs = requerimientos_qs.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if modulo_id:
        requerimientos_qs = requerimientos_qs.filter(modulo_id=modulo_id)
    if prioridad:
        requerimientos_qs = requerimientos_qs.filter(prioridad=prioridad)

    rows = []
    for requerimiento in requerimientos_qs[:50]:
        rows.append({
            'values': [
                requerimiento.codigo,
                requerimiento.nombre,
                requerimiento.modulo.codigo if requerimiento.modulo else '-',
                requerimiento.prioridad or '-',
                _fmt_datetime(requerimiento.fecha_creacion),
            ],
            'actions': _build_actions('requerimiento', requerimiento.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código o nombre'},
        {'type': 'select', 'name': 'modulo', 'label': 'Módulo', 'value': modulo_id, 'options': _select_options(TestModulo.objects.order_by('codigo').values_list('id', 'codigo'))},
        {'type': 'select', 'name': 'prioridad', 'label': 'Prioridad', 'value': prioridad, 'options': _select_options(TestRequerimiento.objects.exclude(prioridad__isnull=True).exclude(prioridad='').values_list('prioridad', flat=True).distinct().order_by('prioridad'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Requerimientos',
        'headers': ['Código', 'Nombre', 'Módulo', 'Prioridad', 'Creación'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_requerimiento_create'),
        'back_url': reverse('pruebastest_index'),
    })


def requerimiento_detail(request, pk):
    requerimiento = get_object_or_404(TestRequerimiento, pk=pk)
    return _detail_entity(request, 'Requerimiento', requerimiento, [
        ('Módulo', requerimiento.modulo),
        ('Código', requerimiento.codigo),
        ('Nombre', requerimiento.nombre),
        ('Descripción', requerimiento.descripcion),
        ('Tipo', requerimiento.tipo),
        ('Prioridad', requerimiento.prioridad),
        ('Estado', requerimiento.estado),
        ('Fecha creación', _fmt_datetime(requerimiento.fecha_creacion)),
    ], 'pruebastest_requerimientos', 'pruebastest_requerimiento_update', 'pruebastest_requerimiento_delete')


def requerimiento_create(request):
    return _save_form(
        request,
        TestRequerimiento,
        ['modulo', 'codigo', 'nombre', 'descripcion', 'tipo', 'prioridad', 'estado'],
        'Nuevo requerimiento',
        'pruebastest_requerimientos',
    )


def requerimiento_update(request, pk):
    requerimiento = get_object_or_404(TestRequerimiento, pk=pk)
    return _save_form(
        request,
        TestRequerimiento,
        ['modulo', 'codigo', 'nombre', 'descripcion', 'tipo', 'prioridad', 'estado'],
        'Editar requerimiento',
        'pruebastest_requerimientos',
        instance=requerimiento,
    )


def requerimiento_delete(request, pk):
    requerimiento = get_object_or_404(TestRequerimiento, pk=pk)
    return _delete_entity(request, requerimiento, 'Eliminar requerimiento', 'pruebastest_requerimientos')


def caso_list(request):
    q = request.GET.get('q', '').strip()
    requerimiento_id = request.GET.get('requerimiento', '').strip()
    estado = request.GET.get('estado', '').strip()
    casos_qs = TestCaso.objects.select_related('requerimiento').order_by('-fecha_creacion')
    if q:
        casos_qs = casos_qs.filter(Q(codigo__icontains=q) | Q(titulo__icontains=q) | Q(descripcion__icontains=q))
    if requerimiento_id:
        casos_qs = casos_qs.filter(requerimiento_id=requerimiento_id)
    if estado:
        casos_qs = casos_qs.filter(estado=estado)

    rows = []
    for caso in casos_qs[:50]:
        rows.append({
            'values': [
                caso.codigo,
                caso.titulo,
                caso.requerimiento.codigo if caso.requerimiento else '-',
                caso.prioridad or '-',
                caso.estado or '-',
            ],
            'actions': _build_actions('caso', caso.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código o título'},
        {'type': 'select', 'name': 'requerimiento', 'label': 'Requerimiento', 'value': requerimiento_id, 'options': _select_options(TestRequerimiento.objects.order_by('codigo').values_list('id', 'codigo'))},
        {'type': 'select', 'name': 'estado', 'label': 'Estado', 'value': estado, 'options': _select_options(TestCaso.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct().order_by('estado'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Casos de prueba',
        'headers': ['Código', 'Título', 'Requerimiento', 'Prioridad', 'Estado'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_caso_create'),
        'back_url': reverse('pruebastest_index'),
    })


def caso_detail(request, pk):
    caso = get_object_or_404(TestCaso, pk=pk)
    return _detail_entity(request, 'Caso de prueba', caso, [
        ('Requerimiento', caso.requerimiento),
        ('Código', caso.codigo),
        ('Título', caso.titulo),
        ('Objetivo', caso.objetivo),
        ('Descripción', caso.descripcion),
        ('Precondiciones', caso.precondiciones),
        ('Datos de prueba', caso.datos_prueba),
        ('Resultado esperado', caso.resultado_esperado),
        ('Prioridad', caso.prioridad),
        ('Tipo', caso.tipo),
        ('Estado', caso.estado),
        ('Versión', caso.version),
        ('Activo', caso.activo),
        ('Fecha creación', _fmt_datetime(caso.fecha_creacion)),
        ('Fecha actualización', _fmt_datetime(caso.fecha_actualizacion)),
    ], 'pruebastest_casos', 'pruebastest_caso_update', 'pruebastest_caso_delete')


def caso_create(request):
    return _save_form(
        request,
        TestCaso,
        ['requerimiento', 'codigo', 'titulo', 'objetivo', 'descripcion', 'precondiciones', 'datos_prueba', 'resultado_esperado', 'prioridad', 'tipo', 'estado', 'version', 'activo'],
        'Nuevo caso de prueba',
        'pruebastest_casos',
    )


def caso_update(request, pk):
    caso = get_object_or_404(TestCaso, pk=pk)
    return _save_form(
        request,
        TestCaso,
        ['requerimiento', 'codigo', 'titulo', 'objetivo', 'descripcion', 'precondiciones', 'datos_prueba', 'resultado_esperado', 'prioridad', 'tipo', 'estado', 'version', 'activo'],
        'Editar caso de prueba',
        'pruebastest_casos',
        instance=caso,
    )


def caso_delete(request, pk):
    caso = get_object_or_404(TestCaso, pk=pk)
    return _delete_entity(request, caso, 'Eliminar caso de prueba', 'pruebastest_casos')


def plan_list(request):
    q = request.GET.get('q', '').strip()
    proyecto_id = request.GET.get('proyecto', '').strip()
    estado = request.GET.get('estado', '').strip()
    planes_qs = TestPlan.objects.select_related('proyecto').order_by('-fecha_creacion')
    if q:
        planes_qs = planes_qs.filter(Q(codigo__icontains=q) | Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if proyecto_id:
        planes_qs = planes_qs.filter(proyecto_id=proyecto_id)
    if estado:
        planes_qs = planes_qs.filter(estado=estado)

    rows = []
    for plan in planes_qs[:50]:
        rows.append({
            'values': [
                plan.codigo,
                plan.nombre,
                plan.proyecto.codigo if plan.proyecto else '-',
                plan.estado or '-',
                _fmt_datetime(plan.fecha_creacion),
            ],
            'actions': _build_actions('plan', plan.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código o nombre'},
        {'type': 'select', 'name': 'proyecto', 'label': 'Proyecto', 'value': proyecto_id, 'options': _select_options(TestProyecto.objects.order_by('codigo').values_list('id', 'codigo'))},
        {'type': 'select', 'name': 'estado', 'label': 'Estado', 'value': estado, 'options': _select_options(TestPlan.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct().order_by('estado'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Planes de prueba',
        'headers': ['Código', 'Nombre', 'Proyecto', 'Estado', 'Creación'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_plan_create'),
        'back_url': reverse('pruebastest_index'),
    })


def plan_detail(request, pk):
    plan = get_object_or_404(TestPlan, pk=pk)
    return _detail_entity(request, 'Plan de prueba', plan, [
        ('Proyecto', plan.proyecto),
        ('Código', plan.codigo),
        ('Nombre', plan.nombre),
        ('Descripción', plan.descripcion),
        ('Versión', plan.version),
        ('Ambiente', plan.ambiente),
        ('Estado', plan.estado),
        ('Fecha inicio', _fmt_date(plan.fecha_inicio)),
        ('Fecha fin', _fmt_date(plan.fecha_fin)),
        ('Responsable', plan.responsable),
        ('Fecha creación', _fmt_datetime(plan.fecha_creacion)),
        ('Fecha actualización', _fmt_datetime(plan.fecha_actualizacion)),
    ], 'pruebastest_planes', 'pruebastest_plan_update', 'pruebastest_plan_delete')


def plan_create(request):
    return _save_form(
        request,
        TestPlan,
        ['proyecto', 'codigo', 'nombre', 'descripcion', 'version', 'ambiente', 'estado', 'fecha_inicio', 'fecha_fin', 'responsable'],
        'Nuevo plan de prueba',
        'pruebastest_planes',
    )


def plan_update(request, pk):
    plan = get_object_or_404(TestPlan, pk=pk)
    return _save_form(
        request,
        TestPlan,
        ['proyecto', 'codigo', 'nombre', 'descripcion', 'version', 'ambiente', 'estado', 'fecha_inicio', 'fecha_fin', 'responsable'],
        'Editar plan de prueba',
        'pruebastest_planes',
        instance=plan,
    )


def plan_delete(request, pk):
    plan = get_object_or_404(TestPlan, pk=pk)
    return _delete_entity(request, plan, 'Eliminar plan de prueba', 'pruebastest_planes')


def ejecucion_list(request):
    q = request.GET.get('q', '').strip()
    resultado = request.GET.get('resultado', '').strip()
    ejecuciones_qs = TestEjecucion.objects.select_related('plan_caso__plan', 'plan_caso__caso').order_by('-fecha_creacion')
    if q:
        ejecuciones_qs = ejecuciones_qs.filter(
            Q(plan_caso__plan__codigo__icontains=q)
            | Q(plan_caso__caso__codigo__icontains=q)
            | Q(observaciones__icontains=q)
            | Q(navegador__icontains=q)
            | Q(sistema_operativo__icontains=q)
        )
    if resultado:
        ejecuciones_qs = ejecuciones_qs.filter(resultado=resultado)

    rows = []
    for ejecucion in ejecuciones_qs[:50]:
        plan_caso = ejecucion.plan_caso
        rows.append({
            'values': [
                ejecucion.id,
                f'{plan_caso.plan.codigo} / {plan_caso.caso.codigo}' if plan_caso and plan_caso.plan and plan_caso.caso else '-',
                ejecucion.resultado or '-',
                _fmt_datetime(ejecucion.fecha_creacion),
            ],
            'actions': _build_actions('ejecucion', ejecucion.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Plan, caso o navegador'},
        {'type': 'select', 'name': 'resultado', 'label': 'Resultado', 'value': resultado, 'options': _select_options(TestEjecucion.objects.exclude(resultado__isnull=True).exclude(resultado='').values_list('resultado', flat=True).distinct().order_by('resultado'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Ejecuciones',
        'headers': ['ID', 'Plan / Caso', 'Resultado', 'Creación'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_ejecucion_create'),
        'back_url': reverse('pruebastest_index'),
    })


def ejecucion_detail(request, pk):
    ejecucion = get_object_or_404(TestEjecucion, pk=pk)
    return _detail_entity(request, 'Ejecución', ejecucion, [
        ('Plan / Caso', ejecucion.plan_caso),
        ('Número ejecución', ejecucion.numero_ejecucion),
        ('Ejecutado por', ejecucion.ejecutado_por),
        ('Fecha inicio', _fmt_datetime(ejecucion.fecha_inicio)),
        ('Fecha fin', _fmt_datetime(ejecucion.fecha_fin)),
        ('Duración segundos', ejecucion.duracion_segundos),
        ('Resultado', ejecucion.resultado),
        ('Observaciones', ejecucion.observaciones),
        ('Navegador', ejecucion.navegador),
        ('Sistema operativo', ejecucion.sistema_operativo),
        ('IP cliente', ejecucion.ip_cliente),
        ('Fecha creación', _fmt_datetime(ejecucion.fecha_creacion)),
    ], 'pruebastest_ejecuciones', 'pruebastest_ejecucion_update', 'pruebastest_ejecucion_delete')


def ejecucion_create(request):
    return _save_form(
        request,
        TestEjecucion,
        ['plan_caso', 'numero_ejecucion', 'ejecutado_por', 'fecha_inicio', 'fecha_fin', 'duracion_segundos', 'resultado', 'observaciones', 'navegador', 'sistema_operativo', 'ip_cliente'],
        'Nueva ejecución',
        'pruebastest_ejecuciones',
    )


def ejecucion_update(request, pk):
    ejecucion = get_object_or_404(TestEjecucion, pk=pk)
    return _save_form(
        request,
        TestEjecucion,
        ['plan_caso', 'numero_ejecucion', 'ejecutado_por', 'fecha_inicio', 'fecha_fin', 'duracion_segundos', 'resultado', 'observaciones', 'navegador', 'sistema_operativo', 'ip_cliente'],
        'Editar ejecución',
        'pruebastest_ejecuciones',
        instance=ejecucion,
    )


def ejecucion_delete(request, pk):
    ejecucion = get_object_or_404(TestEjecucion, pk=pk)
    return _delete_entity(request, ejecucion, 'Eliminar ejecución', 'pruebastest_ejecuciones')


def bug_list(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    severidad = request.GET.get('severidad', '').strip()
    bugs_qs = TestBug.objects.select_related('ejecucion').order_by('-fecha_reporte')
    if q:
        bugs_qs = bugs_qs.filter(Q(codigo__icontains=q) | Q(titulo__icontains=q) | Q(descripcion__icontains=q) | Q(observaciones__icontains=q))
    if estado:
        bugs_qs = bugs_qs.filter(estado=estado)
    if severidad:
        bugs_qs = bugs_qs.filter(severidad=severidad)

    rows = []
    for bug in bugs_qs[:50]:
        rows.append({
            'values': [
                bug.codigo,
                bug.titulo,
                bug.severidad or '-',
                bug.estado or '-',
                _fmt_datetime(bug.fecha_reporte),
            ],
            'actions': _build_actions('bug', bug.pk),
        })

    filter_fields = [
        {'type': 'text', 'name': 'q', 'label': 'Buscar', 'value': q, 'placeholder': 'Código o título'},
        {'type': 'select', 'name': 'estado', 'label': 'Estado', 'value': estado, 'options': _select_options(TestBug.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct().order_by('estado'))},
        {'type': 'select', 'name': 'severidad', 'label': 'Severidad', 'value': severidad, 'options': _select_options(TestBug.objects.exclude(severidad__isnull=True).exclude(severidad='').values_list('severidad', flat=True).distinct().order_by('severidad'))},
    ]
    return render(request, 'pruebastest/entity_list.html', {
        'title': 'Bugs',
        'headers': ['Código', 'Título', 'Severidad', 'Estado', 'Reporte'],
        'rows': rows,
        'filter_fields': filter_fields,
        'create_url': reverse('pruebastest_bug_create'),
        'back_url': reverse('pruebastest_index'),
    })


def bug_detail(request, pk):
    bug = get_object_or_404(TestBug, pk=pk)
    return _detail_entity(request, 'Bug', bug, [
        ('Ejecución', bug.ejecucion),
        ('Código', bug.codigo),
        ('Título', bug.titulo),
        ('Descripción', bug.descripcion),
        ('Severidad', bug.severidad),
        ('Prioridad', bug.prioridad),
        ('Estado', bug.estado),
        ('Responsable', bug.responsable),
        ('Fecha reporte', _fmt_datetime(bug.fecha_reporte)),
        ('Fecha cierre', _fmt_datetime(bug.fecha_cierre)),
        ('Observaciones', bug.observaciones),
    ], 'pruebastest_bugs', 'pruebastest_bug_update', 'pruebastest_bug_delete')


def bug_create(request):
    return _save_form(
        request,
        TestBug,
        ['ejecucion', 'codigo', 'titulo', 'descripcion', 'severidad', 'prioridad', 'estado', 'responsable', 'fecha_reporte', 'fecha_cierre', 'observaciones'],
        'Nuevo bug',
        'pruebastest_bugs',
    )


def bug_update(request, pk):
    bug = get_object_or_404(TestBug, pk=pk)
    return _save_form(
        request,
        TestBug,
        ['ejecucion', 'codigo', 'titulo', 'descripcion', 'severidad', 'prioridad', 'estado', 'responsable', 'fecha_reporte', 'fecha_cierre', 'observaciones'],
        'Editar bug',
        'pruebastest_bugs',
        instance=bug,
    )


def bug_delete(request, pk):
    bug = get_object_or_404(TestBug, pk=pk)
    return _delete_entity(request, bug, 'Eliminar bug', 'pruebastest_bugs')




