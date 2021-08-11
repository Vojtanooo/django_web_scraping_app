from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.home, name="home"),
    path('', views.delete_session, name="delete-session")
]
