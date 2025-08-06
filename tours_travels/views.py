from django.shortcuts import render,HttpResponse
from . import mail as mail_f
from django.template import loader
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest

def home(request):
    return HttpResponse('<h1>Welcome</h1>')

def mail(request):
	mail_f.verification_mail()
	return HttpResponse('<h1>mail is sent</h1>')


# Custom Error Views
def custom_400_view(request, exception=None):
    """Custom 400 Bad Request error page"""
    template = loader.get_template('400.html')
    context = {
        'request_path': request.path,
        'exception': exception,
    }
    return HttpResponseBadRequest(template.render(context, request))


def custom_403_view(request, exception=None):
    """Custom 403 Forbidden error page"""
    template = loader.get_template('403.html')
    context = {
        'request_path': request.path,
        'exception': exception,
    }
    return HttpResponseForbidden(template.render(context, request))


def custom_404_view(request, exception=None):
    """Custom 404 Page Not Found error page"""
    template = loader.get_template('404.html')
    context = {
        'request_path': request.path,
        'exception': exception,
    }
    return HttpResponseNotFound(template.render(context, request))


def custom_500_view(request):
    """Custom 500 Internal Server Error page"""
    template = loader.get_template('500.html')
    context = {
        'request_path': request.path,
    }
    return HttpResponseServerError(template.render(context, request))
