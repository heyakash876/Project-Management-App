from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Project, Task, Comment
from .forms import CustomUserCreationForm, ProjectForm, TaskForm, CommentForm
from django.utils import timezone
from django.views.decorators.http import require_POST
import calendar
from datetime import date
from django.utils.safestring import mark_safe
import json

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html', {})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    projects = Project.objects.filter(team=request.user)
    tasks = Task.objects.filter(project__in=projects)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='done').count()
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0
    recent_tasks = tasks.order_by('-created_at')[:5]
    recent_comments = Comment.objects.filter(task__in=tasks).order_by('-created_at')[:5]
    return render(request, 'dashboard.html', {
        'user': request.user,
        'users': User.objects.all(),
        'projects': projects,
        'progress': progress,
        'recent_tasks': recent_tasks,
        'recent_comments': recent_comments,
    })

@login_required
def projects_dashboard(request):
    projects = Project.objects.filter(team=request.user)
    return render(request, 'projects_dashboard.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()
            return redirect('projects_dashboard')
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    return render(request, 'project_detail.html', {'project': project, 'tasks': tasks})

@login_required
def create_task(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form, 'project': project})

@login_required
def add_comment(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'task': task})

@login_required
def calendar_view(request):
    today = date.today()
    year, month = today.year, today.month
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    calendar_weeks = [[d if d != 0 else None for d in week] for week in month_days]

    tasks = Task.objects.filter(
        assigned_to=request.user,
        due_date__year=year,
        due_date__month=month
    )

    tasks_by_date = {}

    for t in tasks:
        if t.due_date:  # Ensure the task has a due date
            key = str(t.due_date.day)
            if key not in tasks_by_date:
                tasks_by_date[key] = []
            tasks_by_date[key].append({
                'title': t.title,
                'status': t.status,  # use this for logic (e.g. 'done', 'todo')
                'status_display': t.get_status_display(),
                
                'priority': t.priority,  # Must be 'high', 'medium', or 'low'
                'due_date': t.due_date.strftime('%Y-%m-%d'),
            })

    context = {
        'calendar_weeks': calendar_weeks,
        'today': today.day,
        'tasks_by_date': tasks_by_date,
        'tasks_by_date_json': mark_safe(json.dumps(tasks_by_date)),
    }
    return render(request, 'calendar.html', context)


@login_required
@require_POST
def update_task_status(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    new_status = request.POST.get('status')
    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()
    return redirect('project_detail', pk=task.project.pk)

def home(request):
    return redirect('dashboard')