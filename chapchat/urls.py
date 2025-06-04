from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Maps the root of this app's URLs to the home view
]