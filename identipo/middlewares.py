from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse


class RestrictStaffToAdminMiddleware(object):
    """
    A middleware that restricts staff members access to administration panels.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse('admin:index')):
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    raise Http404

        response = self.get_response(request)

        return response


class RestrictSuperuserToDashboardMiddleware(object):
    """
    A middleware that restricts staff members access to administration panels.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse('dashboard_admin:index')):
            if request.user.is_superuser:
                if request.user.is_superuser:
                    return redirect('admin:index')

        response = self.get_response(request)
        return response
