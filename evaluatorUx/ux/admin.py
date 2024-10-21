# admin.py
from django.contrib import admin
from .models import Rubrica, Categoria, Criterio, DescripcionPuntaje, EvaluacionGeneral

class DescripcionPuntajeInline(admin.TabularInline):
    model = DescripcionPuntaje
    extra = 1

class CriterioInline(admin.TabularInline):
    model = Criterio
    extra = 1
    inlines = [DescripcionPuntajeInline]

class CategoriaInline(admin.TabularInline):
    model = Categoria
    extra = 1
    inlines = [CriterioInline]

class RubricaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'predefinida')  # Mostrar el campo predefinida
    list_filter = ('predefinida',)  # Filtro por campo predefinida
    inlines = [CategoriaInline]

admin.site.register(Rubrica, RubricaAdmin)
admin.site.register(Categoria)
admin.site.register(Criterio)
admin.site.register(DescripcionPuntaje)
admin.site.register(EvaluacionGeneral)