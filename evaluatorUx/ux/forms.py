from django import forms
from .models import Rubrica, EvaluacionGeneral, Calificacion

class RubricaForm(forms.ModelForm):
    class Meta:
        model = Rubrica
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full p-2 mb-2 border rounded-lg dark:bg-gray-600 dark:text-white',
                'placeholder': 'Nombre de la rúbrica'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full p-2 mb-2 border rounded-lg dark:bg-gray-600 dark:text-white',
                'placeholder': 'Descripción de la rúbrica'
            }),
        }

class EvaluacionGeneralForm(forms.ModelForm):
    class Meta:
        model = EvaluacionGeneral
        fields = ['nombre_software']
        widgets = {
            'nombre_software': forms.TextInput(attrs={
                'class': 'w-full p-2 m-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg',
                'placeholder': 'Nombre del software'
            }),
        }

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['criterio', 'puntaje', 'comentario']

