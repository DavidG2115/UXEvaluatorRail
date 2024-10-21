from django import forms
from .models import Rubrica, Categoria, Criterio, DescripcionPuntaje
from django.forms import inlineformset_factory

class RubricaForm(forms.ModelForm):
    class Meta:
        model = Rubrica
        fields = ['nombre', 'descripcion']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ['nombre', 'descripcion', 'comentario']

# Crear el formset para agregar varias categorías dinámicamente
CategoriaFormSet = inlineformset_factory(Rubrica, Categoria, form=CategoriaForm, extra=1, can_delete=True)

# Crear el formset para agregar varios criterios dinámicamente dentro de cada categoría
CriterioFormSet = inlineformset_factory(Categoria, Criterio, form=CriterioForm, extra=1, can_delete=True)
