from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):

    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.is_staff:
            raise PermissionDenied()

        return view_func(request, *args, **kwargs)

    return wrapper
