from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'), 
    path('login/', login_view, name='login'),
    path('registro/', register_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('crear/', crear_rubrica, name='crear_rubrica'),
    path('seleccionar/', seleccionar_rubrica, name='seleccionar_rubrica'),
    path('ver/<int:rubrica_id>/', ver_rubrica, name='ver_rubrica'),
    path('editar/<int:rubrica_id>/', editar_rubrica, name='editar_rubrica'),
    path('eliminar/<int:rubrica_id>/', eliminar_rubrica, name='eliminar_rubrica'),
    path('rubrica/<int:rubrica_id>/evaluar/', realizar_evaluacion, name='realizar_evaluacion'),
    path('evaluacion/<int:evaluacion_id>/', ver_evaluacion, name='ver_evaluacion'),
    path('evaluacion/<int:evaluacion_id>/pdf/', generar_pdf, name='generar_pdf'),
    path('generar_pdf_con_grafico/<int:evaluacion_id>/', generar_pdf_con_grafico, name='generar_pdf_con_grafico'),
    path('eliminar_evaluacion/<int:evaluacion_id>/', eliminar_evaluacion, name='eliminar_evaluacion'),
]