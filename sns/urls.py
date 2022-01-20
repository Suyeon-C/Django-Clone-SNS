from django.urls import path
from .views import *

app_name = 'sns'

urlpatterns = [
    path('', Main.as_view(), name='main'),
]