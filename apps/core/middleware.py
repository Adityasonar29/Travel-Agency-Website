from django.http import Http404
from django.shortcuts import render


class Voyage404Middleware:
    """Render the branded 404 page for view-level Http404 responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Http404:
            return render(request, '404.html', status=404)

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return render(request, '404.html', status=404)
        return None
