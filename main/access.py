from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


def public_post(view_func):
    """Keep prototype endpoints public while enforcing POST + CSRF semantics."""
    return csrf_protect(require_POST(view_func))
