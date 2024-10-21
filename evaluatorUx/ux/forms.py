from django import forms
from .models import Rubrica, EvaluacionGeneral, Calificacion

class RubricaForm(forms.ModelForm):
    class Meta:
        model = Rubrica
        fields = ['nombre', 'descripcion']

class EvaluacionGeneralForm(forms.ModelForm):
    class Meta:
        model = EvaluacionGeneral
        fields = ['nombre_software']

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['criterio', 'puntaje', 'comentario']

