from django.urls import path
from . import views 

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.home_redirect_view, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    ## PADRON NOMINAL SITUACION
]