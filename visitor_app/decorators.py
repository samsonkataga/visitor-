from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'visitor_app/access_denied.html', {
                'message': 'Please log in to access this page.'
            })
        if not request.user.is_staff:
            return render(request, 'visitor_app/access_denied.html', {
                'message': 'Access denied. Admin privileges required.'
            })
        return view_func(request, *args, **kwargs)
    return _wrapped_view