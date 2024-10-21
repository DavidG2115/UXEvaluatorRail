from django.shortcuts import render, redirect
from django.contrib import messages  # Import the messages module
from .forms import RubricaForm, CategoriaFormSet, CriterioFormSet
from .models import Criterio, Categoria, Rubrica  # Import the Rubrica and Categoria models

# Create your views here.
def index(request):
    return render(request, 'rubricas/index.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import modelform_factory
from .models import Rubrica, Categoria, Criterio


def crear_rubrica(request):
    if request.method == "POST":
        # Crear la rúbrica
        nombre_rubrica = request.POST.get('nombre_rubrica')
        descripcion_rubrica = request.POST.get('descripcion_rubrica')

        rubrica = Rubrica.objects.create(nombre=nombre_rubrica, descripcion=descripcion_rubrica, usuario=request.user)

        # Obtener el número de categorías
        categorias_count = int(request.POST.get('categorias_count', 0))

        # Iterar sobre las categorías dinámicas
        for i in range(categorias_count):
            nombre_categoria = request.POST.get(f'categorias-{i}-nombre')
            descripcion_categoria = request.POST.get(f'categorias-{i}-descripcion')

            if nombre_categoria:  # Asegurarse de que el nombre no esté vacío
                categoria = Categoria.objects.create(rubrica=rubrica, nombre=nombre_categoria, descripcion=descripcion_categoria)

                # Obtener el número de criterios para esta categoría
                criterios_count = int(request.POST.get(f'criterios_count-{i}', 0))

                # Iterar sobre los criterios dinámicos
                for j in range(criterios_count):
                    nombre_criterio = request.POST.get(f'criterios-{i}-{j}-nombre')
                    descripcion_criterio = request.POST.get(f'criterios-{i}-{j}-descripcion')
                    comentario_criterio = request.POST.get(f'criterios-{i}-{j}-comentario')

                    if nombre_criterio:  # Asegurarse de que el nombre del criterio no esté vacío
                        Criterio.objects.create(
                            categoria=categoria,
                            nombre=nombre_criterio,
                            descripcion=descripcion_criterio,
                            comentario=comentario_criterio
                        )

        return redirect('seleccionar_rubrica')  # Redirigir a una vista donde se liste las rúbricas

    return render(request, 'rubricas/crear.html')




def seleccionar_rubrica(request):
    rubricas = Rubrica.objects.all()  # Mostrar todas las rúbricas
    
    if request.method == 'POST':
        rubrica_id = request.POST.get('rubrica_id')
        if rubrica_id:
            return redirect('editar_rubrica', rubrica_id=rubrica_id)
        else:
            messages.error(request, "Debes seleccionar una rúbrica.")

    return render(request, 'rubricas/seleccionar.html', {'rubricas': rubricas})

def ver_rubrica(request, rubrica_id):
    rubrica = Rubrica.objects.get(id=rubrica_id)

    # Obtiene todas las categorías asociadas a la rúbrica usando el related_name
    categorias = rubrica.categorias.all()

    # Prepara las categorías con sus criterios
    categorias_con_criterios = []
    for categoria in categorias:
        criterios = categoria.criterios.all()  # Usa el related_name para acceder a los criterios
        categorias_con_criterios.append({
            'categoria': categoria,
            'criterios': criterios
        })

    return render(request, 'rubricas/ver_rubrica.html', {
        'rubrica': rubrica,
        'categorias_con_criterios': categorias_con_criterios
    })
