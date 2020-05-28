from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect
from django.http import HttpResponse


def donatehome(request):
    context = {}
    print("Reached here")
    return render(request, 'donate/templates/donate_home.html', context)
