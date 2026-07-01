import ast
from datetime import date

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import DeveloperPerformance, FollowUp, Observation, PriorityActivity, Project, Status, Task


class ProjectListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Project
    template_name = 'home/project_list.html'
    context_object_name = 'projects'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Project
    fields = ['name', 'description', 'status']
    template_name = 'home/project_form.html'
    success_url = reverse_lazy('project_list')


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Project
    fields = ['name', 'description', 'status']
    template_name = 'home/project_form.html'
    success_url = reverse_lazy('project_list')


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Project
    template_name = 'home/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')


class TaskListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Task
    template_name = 'home/task_list.html'
    context_object_name = 'tasks'


class TaskCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = Task
    fields = ['title', 'description', 'project', 'status', 'assigned_to', 'priority', 'due_date']
    template_name = 'home/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Task
    fields = ['title', 'description', 'project', 'status', 'assigned_to', 'priority', 'due_date']
    template_name = 'home/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Task
    template_name = 'home/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')


class FollowUpListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = FollowUp
    template_name = 'home/followup_list.html'
    context_object_name = 'followups'


class FollowUpCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = FollowUp
    fields = ['task', 'comment', 'created_by']
    template_name = 'home/followup_form.html'
    success_url = reverse_lazy('followup_list')


class FollowUpUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = FollowUp
    fields = ['task', 'comment', 'created_by']
    template_name = 'home/followup_form.html'
    success_url = reverse_lazy('followup_list')


class FollowUpDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = FollowUp
    template_name = 'home/followup_confirm_delete.html'
    success_url = reverse_lazy('followup_list')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'home/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    total_projects = Project.objects.count()
    total_tasks = Task.objects.count()
    total_followups = FollowUp.objects.count()
    statuses = Status.objects.filter(category='task').annotate(task_count=Count('tasks'))
    recent_tasks = Task.objects.select_related('project', 'status', 'assigned_to').order_by('-created_at')[:8]
    performance_records = DeveloperPerformance.objects.select_related('developer').order_by('-week_start')[:6]
    observations = Observation.objects.select_related('developer', 'task').order_by('-created_at')[:6]
    users = get_user_model().objects.annotate(task_count=Count('tasks')).order_by('username')
    workflow_stages = [
        {'name': 'Análisis', 'description': 'Requerimientos, diseño y definición', 'count': Task.objects.filter(Q(status__name__icontains='anal') | Q(status__name__icontains='diseñ') | Q(status__name__icontains='disen') | Q(status__name__icontains='requis') | Q(status__name__icontains='backlog') | Q(status__name__icontains='pendiente') | Q(status__name__icontains='por hacer')).count()},
        {'name': 'Implementación', 'description': 'Construcción y desarrollo del servicio', 'count': Task.objects.filter(Q(status__name__icontains='desarrollo') | Q(status__name__icontains='implement') | Q(status__name__icontains='progreso') | Q(status__name__icontains='en curso') | Q(status__name__icontains='avance')).count()},
        {'name': 'QA', 'description': 'Pruebas funcionales y revisión', 'count': Task.objects.filter(Q(status__name__icontains='prueba') | Q(status__name__icontains='testing') | Q(status__name__icontains='qa') | Q(status__name__icontains='revisión') | Q(status__name__icontains='revision')).count()},
        {'name': 'Producción', 'description': 'Aprobación y publicación final', 'count': Task.objects.filter(Q(status__name__icontains='producc') | Q(status__name__icontains='public') | Q(status__name__icontains='deploy') | Q(status__name__icontains='release') | Q(status__name__icontains='aprob') | Q(status__name__icontains='valid') | Q(status__name__icontains='listo') | Q(status__name__icontains='cerrad') | Q(status__name__icontains='done')).count()},
    ]
    user_summary = []
    for user in users:
        assigned_tasks = Task.objects.filter(assigned_to=user)
        completed_tasks = assigned_tasks.filter(status__name__icontains='done')
        latest_record = DeveloperPerformance.objects.filter(developer=user).order_by('-week_start').first()
        progress = latest_record.progress_percentage if latest_record else 0
        if not progress and assigned_tasks.exists():
            progress = round((completed_tasks.count() / assigned_tasks.count()) * 100, 1) if assigned_tasks.count() else 0
        user_summary.append({
            'user': user,
            'tasks_count': assigned_tasks.count(),
            'completed_tasks': completed_tasks.count(),
            'progress': progress,
            'latest_record': latest_record,
        })

    context = {
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'total_followups': total_followups,
        'statuses': statuses,
        'recent_tasks': recent_tasks,
        'performance_records': performance_records,
        'observations': observations,
        'workflow_stages': workflow_stages,
        'user_summary': user_summary,
    }
    return render(request, 'home/dashboard.html', context)


@login_required(login_url='login')
def user_list(request):
    users = get_user_model().objects.annotate(task_count=Count('tasks')).order_by('username')
    return render(request, 'home/user_list.html', {'users': users})


@login_required(login_url='login')
def create_status(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'task')
        color = request.POST.get('color', 'secondary')
        if name:
            Status.objects.create(name=name, category=category, color=color)
            return redirect('dashboard')
    statuses = Status.objects.all()
    return render(request, 'home/status_form.html', {'statuses': statuses})


@login_required(login_url='login')
def productivity_dashboard(request):
    selected_developer = request.GET.get('developer', '')
    selected_week = request.GET.get('week', '')

    performance = DeveloperPerformance.objects.select_related('developer').order_by('developer__username', '-week_start')
    if selected_developer:
        performance = performance.filter(developer_id=selected_developer)
    if selected_week:
        performance = performance.filter(week_start=selected_week)

    users = get_user_model().objects.annotate(task_count=Count('tasks')).order_by('username')
    observations = Observation.objects.select_related('developer', 'task').order_by('-created_at')
    chart_data = []
    dev_summary = []
    trend_data = []
    summary_users = users
    if selected_developer:
        summary_users = summary_users.filter(id=selected_developer)

    for user in summary_users:
        latest_record = DeveloperPerformance.objects.filter(developer=user).order_by('-week_start').first()
        if selected_week:
            latest_record = DeveloperPerformance.objects.filter(developer=user, week_start=selected_week).order_by('-week_start').first()
        assigned_tasks = Task.objects.filter(assigned_to=user)
        if selected_week:
            assigned_tasks = assigned_tasks.filter(created_at__date__lte=selected_week)
        completed_tasks = assigned_tasks.filter(status__name__icontains='done')
        progress = 0
        if latest_record:
            progress = latest_record.progress_percentage or latest_record.performance_ratio
        elif assigned_tasks.exists():
            progress = round((completed_tasks.count() / assigned_tasks.count()) * 100, 1) if assigned_tasks.count() else 0
        dev_summary.append({
            'user': user,
            'tasks_count': assigned_tasks.count(),
            'completed_tasks': completed_tasks.count(),
            'progress': progress,
            'latest_record': latest_record,
        })

    for record in performance:
        chart_data.append({
            'name': record.developer.username,
            'quota': record.quota_services,
            'completed': record.completed_services,
            'percentage': record.performance_ratio,
        })

    for user in summary_users:
        developer_history = DeveloperPerformance.objects.filter(developer=user).order_by('week_start')
        if selected_week:
            developer_history = developer_history.filter(week_start=selected_week)
        points = []
        for record in developer_history:
            value = record.progress_percentage or record.performance_ratio
            points.append({'week': record.week_start.strftime('%d/%m'), 'value': value})

        max_value = max((point['value'] for point in points), default=100) or 100
        svg_points = []
        for index, point in enumerate(points):
            x = 10 + (index * 80 / max(1, len(points) - 1)) if len(points) > 1 else 50
            y = 90 - ((point['value'] / max_value) * 70)
            point['x'] = round(x, 1)
            point['y'] = round(y, 1)
            svg_points.append(f'{point["x"]:.1f},{point["y"]:.1f}')
        trend_data.append({
            'name': user.username,
            'points': points,
            'points_svg': ' '.join(svg_points),
        })

    context = {
        'performance': performance,
        'users': users,
        'observations': observations,
        'chart_data': chart_data,
        'dev_summary': dev_summary,
        'trend_data': trend_data,
        'selected_developer': selected_developer,
        'selected_week': selected_week,
        'weeks': DeveloperPerformance.objects.values_list('week_start', flat=True).distinct().order_by('-week_start'),
    }
    return render(request, 'home/productivity_dashboard.html', context)


@login_required(login_url='login')
def register_performance(request):
    if request.method == 'POST':
        developer_id = request.POST.get('developer')
        week_start = request.POST.get('week_start')
        quota_services = request.POST.get('quota_services', 0)
        completed_services = request.POST.get('completed_services', 0)
        progress_percentage = request.POST.get('progress_percentage', 0)
        notes = request.POST.get('notes', '')
        if developer_id and week_start:
            DeveloperPerformance.objects.create(
                developer_id=developer_id,
                week_start=week_start,
                quota_services=int(quota_services or 0),
                completed_services=int(completed_services or 0),
                progress_percentage=int(progress_percentage or 0),
                notes=notes,
            )
            return redirect('productivity_dashboard')
    users = get_user_model().objects.all().order_by('username')
    return render(request, 'home/performance_form.html', {'users': users})


@login_required(login_url='login')
def create_observation(request):
    if request.method == 'POST':
        developer_id = request.POST.get('developer')
        task_id = request.POST.get('task')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        severity = request.POST.get('severity', 'medium')
        if developer_id and title:
            Observation.objects.create(
                developer_id=developer_id,
                task_id=task_id or None,
                title=title,
                description=description,
                severity=severity,
            )
            return redirect('productivity_dashboard')
    users = get_user_model().objects.all().order_by('username')
    tasks = Task.objects.select_related('project').order_by('-created_at')
    return render(request, 'home/observation_form.html', {'users': users, 'tasks': tasks})


@login_required(login_url='login')
def priority_activities(request):
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    selected_priority = request.GET.get('priority', '')
    selected_status = request.GET.get('status', '')

    activities_qs = PriorityActivity.objects.select_related('assigned_to').all()
    if selected_priority:
        activities_qs = activities_qs.filter(priority=selected_priority)
    if selected_status:
        activities_qs = activities_qs.filter(status=selected_status)

    activities = sorted(activities_qs, key=lambda item: (priority_order.get(item.priority, 99), item.due_date or date.max, item.created_at))

    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        if activity_id:
            activity = get_object_or_404(PriorityActivity, pk=activity_id)
        else:
            activity = PriorityActivity()

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'high')
        status = request.POST.get('status', 'pending')
        assigned_to_id = request.POST.get('assigned_to') or None
        due_date = request.POST.get('due_date') or None
        if title:
            activity.title = title
            activity.description = description
            activity.priority = priority
            activity.status = status
            activity.assigned_to_id = assigned_to_id
            activity.due_date = due_date
            activity.save()
            return redirect('priority_activities')

    users = get_user_model().objects.all().order_by('username')
    status_summary = [
        {'label': 'Pendientes', 'value': activities_qs.filter(status='pending').count(), 'code': 'pending'},
        {'label': 'En progreso', 'value': activities_qs.filter(status='in_progress').count(), 'code': 'in_progress'},
        {'label': 'Completadas', 'value': activities_qs.filter(status='done').count(), 'code': 'done'},
    ]
    priority_summary = [
        {'label': 'Críticas', 'value': activities_qs.filter(priority='critical').count(), 'code': 'critical'},
        {'label': 'Altas', 'value': activities_qs.filter(priority='high').count(), 'code': 'high'},
        {'label': 'Medias', 'value': activities_qs.filter(priority='medium').count(), 'code': 'medium'},
        {'label': 'Bajas', 'value': activities_qs.filter(priority='low').count(), 'code': 'low'},
    ]
    return render(request, 'home/priority_activities.html', {
        'activities': activities,
        'users': users,
        'status_summary': status_summary,
        'priority_summary': priority_summary,
        'editing_activity': None,
        'selected_priority': selected_priority,
        'selected_status': selected_status,
    })


@login_required(login_url='login')
def priority_activity_update(request, pk):
    activity = get_object_or_404(PriorityActivity, pk=pk)
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    activities_qs = PriorityActivity.objects.select_related('assigned_to').all()
    activities = sorted(activities_qs, key=lambda item: (priority_order.get(item.priority, 99), item.due_date or date.max, item.created_at))

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'high')
        status = request.POST.get('status', 'pending')
        assigned_to_id = request.POST.get('assigned_to') or None
        due_date = request.POST.get('due_date') or None
        if title:
            activity.title = title
            activity.description = description
            activity.priority = priority
            activity.status = status
            activity.assigned_to_id = assigned_to_id
            activity.due_date = due_date
            activity.save()
            return redirect('priority_activities')

    users = get_user_model().objects.all().order_by('username')
    status_summary = [
        {'label': 'Pendientes', 'value': activities_qs.filter(status='pending').count(), 'code': 'pending'},
        {'label': 'En progreso', 'value': activities_qs.filter(status='in_progress').count(), 'code': 'in_progress'},
        {'label': 'Completadas', 'value': activities_qs.filter(status='done').count(), 'code': 'done'},
    ]
    priority_summary = [
        {'label': 'Críticas', 'value': activities_qs.filter(priority='critical').count(), 'code': 'critical'},
        {'label': 'Altas', 'value': activities_qs.filter(priority='high').count(), 'code': 'high'},
        {'label': 'Medias', 'value': activities_qs.filter(priority='medium').count(), 'code': 'medium'},
        {'label': 'Bajas', 'value': activities_qs.filter(priority='low').count(), 'code': 'low'},
    ]
    return render(request, 'home/priority_activities.html', {
        'activities': activities,
        'users': users,
        'status_summary': status_summary,
        'priority_summary': priority_summary,
        'editing_activity': activity,
        'selected_priority': '',
        'selected_status': '',
    })


@login_required(login_url='login')
def priority_activity_delete(request, pk):
    activity = get_object_or_404(PriorityActivity, pk=pk)
    if request.method == 'POST':
        activity.delete()
    return redirect('priority_activities')


@login_required(login_url='login')
def priority_activity_status_update(request, pk):
    activity = get_object_or_404(PriorityActivity, pk=pk)
    if request.method == 'POST':
        new_status = (
            request.POST.get('status')
            or request.POST.get('new_status')
            or request.POST.get('column', '')
        ).strip()
        if not new_status and request.body:
            try:
                payload = ast.literal_eval(request.body.decode())
            except (ValueError, SyntaxError):
                payload = None
            if isinstance(payload, dict):
                new_status = (
                    payload.get('status')
                    or payload.get('new_status')
                    or payload.get('column', '')
                ).strip()
        valid_statuses = {code for code, _label in PriorityActivity.STATUS_CHOICES}
        if new_status in valid_statuses:
            activity.status = new_status
            activity.save()
    return JsonResponse({'status': activity.status})
