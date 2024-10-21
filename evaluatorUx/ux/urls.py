from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('crear/', crear_rubrica, name='crear_rubrica'),
    path('seleccionar/', seleccionar_rubrica, name='seleccionar_rubrica'),
    path('ver/<int:rubrica_id>/', ver_rubrica, name='ver_rubrica'),
]