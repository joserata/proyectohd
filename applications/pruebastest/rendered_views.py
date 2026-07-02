from django.shortcuts import render

from .models import (
    TestBug,
    TestCaso,
    TestEjecucion,
    TestModulo,
    TestPlan,
    TestProyecto,
    TestRequerimiento,
)


def _fmt_datetime(value):
    if not value:
        return '-'
    return value.strftime('%Y-%m-%d %H:%M')


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
    return render(request, 'pruebastest/index.html', {'stats': stats, 'sections': sections})


def proyecto_list(request):
    proyectos = TestProyecto.objects.order_by('-fecha_creacion')[:20]
    rows = [
        (
            p.codigo,
            p.nombre,
            p.estado or '-',
            p.cliente or '-',
            _fmt_datetime(p.fecha_creacion),
        )
        for p in proyectos
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Proyectos',
        'headers': ['Código', 'Nombre', 'Estado', 'Cliente', 'Creación'],
        'rows': rows,
    })


def modulo_list(request):
    modulos = TestModulo.objects.select_related('proyecto').order_by('-fecha_creacion')[:20]
    rows = [
        (
            m.codigo,
            m.nombre,
            m.proyecto.codigo if m.proyecto else '-',
            m.estado or '-',
            _fmt_datetime(m.fecha_creacion),
        )
        for m in modulos
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Módulos',
        'headers': ['Código', 'Nombre', 'Proyecto', 'Estado', 'Creación'],
        'rows': rows,
    })


def requerimiento_list(request):
    requerimientos = TestRequerimiento.objects.select_related('modulo').order_by('-fecha_creacion')[:20]
    rows = [
        (
            r.codigo,
            r.nombre,
            r.modulo.codigo if r.modulo else '-',
            r.prioridad or '-',
            _fmt_datetime(r.fecha_creacion),
        )
        for r in requerimientos
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Requerimientos',
        'headers': ['Código', 'Nombre', 'Módulo', 'Prioridad', 'Creación'],
        'rows': rows,
    })


def caso_list(request):
    casos = TestCaso.objects.select_related('requerimiento').order_by('-fecha_creacion')[:20]
    rows = [
        (
            c.codigo,
            c.titulo,
            c.requerimiento.codigo if c.requerimiento else '-',
            c.prioridad or '-',
            c.estado or '-',
        )
        for c in casos
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Casos de prueba',
        'headers': ['Código', 'Título', 'Requerimiento', 'Prioridad', 'Estado'],
        'rows': rows,
    })


def plan_list(request):
    planes = TestPlan.objects.select_related('proyecto').order_by('-fecha_creacion')[:20]
    rows = [
        (
            p.codigo,
            p.nombre,
            p.proyecto.codigo if p.proyecto else '-',
            p.estado or '-',
            _fmt_datetime(p.fecha_creacion),
        )
        for p in planes
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Planes de prueba',
        'headers': ['Código', 'Nombre', 'Proyecto', 'Estado', 'Creación'],
        'rows': rows,
    })


def ejecucion_list(request):
    ejecuciones = TestEjecucion.objects.select_related('plan_caso__plan', 'plan_caso__caso').order_by('-fecha_creacion')[:20]
    rows = [
        (
            e.id,
            f'{e.plan_caso.plan.codigo} / {e.plan_caso.caso.codigo}' if e.plan_caso and e.plan_caso.plan and e.plan_caso.caso else '-',
            e.resultado or '-',
            _fmt_datetime(e.fecha_creacion),
        )
        for e in ejecuciones
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Ejecuciones',
        'headers': ['ID', 'Plan / Caso', 'Resultado', 'Creación'],
        'rows': rows,
    })


def bug_list(request):
    bugs = TestBug.objects.select_related('ejecucion').order_by('-fecha_reporte')[:20]
    rows = [
        (
            b.codigo,
            b.titulo,
            b.severidad or '-',
            b.estado or '-',
            _fmt_datetime(b.fecha_reporte),
        )
        for b in bugs
    ]
    return render(request, 'pruebastest/list.html', {
        'title': 'Bugs',
        'headers': ['Código', 'Título', 'Severidad', 'Estado', 'Reporte'],
        'rows': rows,
    })
