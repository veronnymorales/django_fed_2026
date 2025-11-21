from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.db import IntegrityError

from base.models import Actualizacion


# Create your views here.
def BASE(request):
    actualizacion = Actualizacion.objects.all()
    return render(request, 'base.html', {"actualizacion": actualizacion})


def inicio(request):
    actualizacion = Actualizacion.objects.all()
    return render(request, 'index.html', {"actualizacion": actualizacion})


def home_redirect_view(request):

    return redirect('signin')

# ----- INICIO DE SESION --------------------------------
@login_required
def signout(request):
    logout(request)
    return redirect('signin')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('inicio')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home_dashboard')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'Usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'Password fo not match'
        })

