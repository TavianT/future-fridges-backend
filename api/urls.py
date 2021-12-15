from . import views
from django.urls import path
urlpatterns = [
    path('users/', views.allUsers, name="users"),
    path('user/<str:pk>/', views.singleUser, name="user"),
]