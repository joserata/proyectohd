from functools import wraps

from django.shortcuts import redirect

ROLE_HOME = {
    'developer': 'dashboard',
    'tester': 'pruebastest_index',
    'security': 'security:dashboard',
}

ROLE_LABELS = {
    'developer': 'Desarrollo',
    'tester': 'Tester',
    'security': 'security',
}

ROLE_CHOICES = (
    ('developer', 'Desarrollo'),
    ('tester', 'Tester'),
    ('security', 'Security'),
)


def get_profile(request):
    profile = request.session.get('user_profile')
    if profile in ROLE_HOME:
        return profile
    path = getattr(request, 'path', '') or ''
    if path.startswith('/pruebastest/'):
        return 'tester'
    return 'developer'


def profile_home(profile):
    return ROLE_HOME.get(profile, 'dashboard')


def profile_required(*allowed_profiles):
    allowed = set(allowed_profiles)

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            profile = get_profile(request)
            if profile not in allowed:
                return redirect(profile_home(profile))

            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
