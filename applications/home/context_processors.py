from .role_utils import get_profile


def active_profile(request):
    return {'user_profile': get_profile(request)}
