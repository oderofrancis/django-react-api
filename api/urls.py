from django.urls import path
from .views import *

urlpatterns = [
    path('todos/', TodoList.as_view()),
]