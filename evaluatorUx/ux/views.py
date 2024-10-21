from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import the messages module
from .forms import RubricaForm, EvaluacionGeneralForm, CalificacionForm  # Import the RubricaForm
from .models import Criterio, Categoria, Rubrica, DescripcionPuntaje, Calificacion, EvaluacionGeneral  # Import the Rubrica and Categoria models

# Create your views here.
def index(request):
    return render(request, 'rubricas/index.html')

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

                    if nombre_criterio:  # Asegurarse de que el nombre del criterio no esté vacío
                        criterio = Criterio.objects.create(
                            categoria=categoria,
                            nombre=nombre_criterio,
                            descripcion=descripcion_criterio
                        )

                        # Crear las descripciones de los puntajes
                        for puntaje in range(1, 6):  # Puntajes del 1 al 5
                            descripcion_puntaje = request.POST.get(f'criterios-{i}-{j}-puntaje-{puntaje}')
                            if descripcion_puntaje:
                                DescripcionPuntaje.objects.create(
                                    criterio=criterio,
                                    puntaje=puntaje,
                                    descripcion=descripcion_puntaje
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
    rubrica = get_object_or_404(Rubrica, id=rubrica_id)
    categorias = Categoria.objects.filter(rubrica=rubrica).prefetch_related('criterios__descripciones')

    categorias_con_criterios = []
    
    for categoria in categorias:
        criterios_con_puntajes = []
        for criterio in categoria.criterios.all():
            # Creamos un diccionario con las descripciones de cada puntaje
            descripciones_puntajes = {
                1: criterio.descripciones.filter(puntaje=1).first(),
                2: criterio.descripciones.filter(puntaje=2).first(),
                3: criterio.descripciones.filter(puntaje=3).first(),
                4: criterio.descripciones.filter(puntaje=4).first(),
                5: criterio.descripciones.filter(puntaje=5).first(),
            }
            criterios_con_puntajes.append({
                'criterio': criterio,
                'descripciones_puntajes': descripciones_puntajes,
            })
        
        categorias_con_criterios.append({
            'categoria': categoria,
            'criterios': criterios_con_puntajes,
        })

    context = {
        'rubrica': rubrica,
        'categorias_con_criterios': categorias_con_criterios,
    }
    
    return render(request, 'rubricas/ver_rubrica.html', context)

def editar_rubrica(request, rubrica_id):
    rubrica = get_object_or_404(Rubrica, id=rubrica_id)
    
    if request.method == 'POST':
        rubrica_form = RubricaForm(request.POST, instance=rubrica)
        if rubrica_form.is_valid():
            rubrica_form.save()

            # Guardar cambios de las categorías
            categorias = Categoria.objects.filter(rubrica=rubrica)

            for categoria in categorias:
                if request.POST.get(f'eliminar_categoria_{categoria.id}') == 'true':
                    categoria.delete()
                    continue

                categoria_nombre = request.POST.get(f'categoria_nombre_{categoria.id}')
                categoria_descripcion = request.POST.get(f'categoria_descripcion_{categoria.id}')

                if categoria_nombre:  # Solo actualiza si no está vacío
                    categoria.nombre = categoria_nombre
                    categoria.descripcion = categoria_descripcion
                    categoria.save()

                    # Guardar cambios de los criterios dentro de la categoría
                    for criterio in categoria.criterios.all():
                        if request.POST.get(f'eliminar_criterio_{criterio.id}') == 'true':
                            criterio.delete()
                            continue

                        criterio_nombre = request.POST.get(f'criterio_nombre_{criterio.id}')
                        criterio_descripcion = request.POST.get(f'criterio_descripcion_{criterio.id}')

                        if criterio_nombre:  # Solo actualiza si no está vacío
                            criterio.nombre = criterio_nombre
                            criterio.descripcion = criterio_descripcion
                            criterio.save()

                            # Guardar descripciones de puntajes
                            for puntaje in range(1, 6):  # Puntajes del 1 al 5
                                descripcion_puntaje = request.POST.get(f'descripcion_puntaje_{criterio.id}_{puntaje}')
                                if descripcion_puntaje:  # Verifica que no sea vacío
                                    descripcion_objeto, _ = DescripcionPuntaje.objects.get_or_create(
                                        criterio=criterio, puntaje=puntaje
                                    )
                                    descripcion_objeto.descripcion = descripcion_puntaje
                                    descripcion_objeto.save()

            # Crear nuevas categorías si se han agregado
            nuevas_categorias_nombres = request.POST.getlist('nueva_categoria_nombre[]')
            nuevas_categorias_descripciones = request.POST.getlist('nueva_categoria_descripcion[]')

            for nombre, descripcion in zip(nuevas_categorias_nombres, nuevas_categorias_descripciones):
                if nombre:  # Solo crea si no está vacío
                    nueva_categoria = Categoria.objects.create(rubrica=rubrica, nombre=nombre, descripcion=descripcion)

                    # Crear nuevos criterios para la nueva categoría
                    nuevos_criterios_nombres = request.POST.getlist(f'nuevo_criterio_nombre_{nueva_categoria.id}[]')
                    nuevos_criterios_descripciones = request.POST.getlist(f'nuevo_criterio_descripcion_{nueva_categoria.id}[]')

                    for criterio_nombre, criterio_descripcion in zip(nuevos_criterios_nombres, nuevos_criterios_descripciones):
                        if criterio_nombre:
                            nuevo_criterio = Criterio.objects.create(categoria=nueva_categoria, nombre=criterio_nombre, descripcion=criterio_descripcion)

                            # Crear descripciones de puntajes para el nuevo criterio
                            for puntaje in range(1, 6):
                                descripcion_puntaje = request.POST.get(f'descripcion_puntaje_nuevo_{nueva_categoria.id}_{puntaje}[]')
                                if descripcion_puntaje:
                                    DescripcionPuntaje.objects.create(
                                        criterio=nuevo_criterio,
                                        puntaje=puntaje,
                                        descripcion=descripcion_puntaje
                                    )

            # Crear nuevos criterios para las categorías existentes
            for categoria in categorias:
                nuevos_criterios_nombres = request.POST.getlist(f'nuevo_criterio_nombre_{categoria.id}[]')
                nuevos_criterios_descripciones = request.POST.getlist(f'nuevo_criterio_descripcion_{categoria.id}[]')

                for criterio_nombre, criterio_descripcion in zip(nuevos_criterios_nombres, nuevos_criterios_descripciones):
                    if criterio_nombre:
                        nuevo_criterio = Criterio.objects.create(categoria=categoria, nombre=criterio_nombre, descripcion=criterio_descripcion)

                        # Crear descripciones de puntajes para el nuevo criterio
                        for puntaje in range(1, 6):
                            descripcion_puntaje = request.POST.get(f'descripcion_puntaje_nuevo_{categoria.id}_{puntaje}[]')
                            if descripcion_puntaje:
                                DescripcionPuntaje.objects.create(
                                    criterio=nuevo_criterio,
                                    puntaje=puntaje,
                                    descripcion=descripcion_puntaje
                                )

            return redirect('ver_rubrica', rubrica_id=rubrica.id)

    else:
        rubrica_form = RubricaForm(instance=rubrica)

    categorias = Categoria.objects.filter(rubrica=rubrica).prefetch_related('criterios__descripciones')

    context = {
        'rubrica': rubrica,
        'rubrica_form': rubrica_form,
        'categorias': categorias,
    }
    return render(request, 'rubricas/editar_rubrica.html', context)

def eliminar_rubrica(request, rubrica_id):
    rubrica = get_object_or_404(Rubrica, id=rubrica_id)
    rubrica.delete()
    return redirect('seleccionar_rubrica')



# views.py
def realizar_evaluacion(request, rubrica_id):
    rubrica = get_object_or_404(Rubrica, id=rubrica_id)
    categorias = Categoria.objects.filter(rubrica=rubrica).prefetch_related('criterios__descripciones')

    if request.method == 'POST':
        evaluacion_general_form = EvaluacionGeneralForm(request.POST)
        if evaluacion_general_form.is_valid():
            evaluacion_general = evaluacion_general_form.save(commit=False)
            evaluacion_general.rubrica = rubrica
            evaluacion_general.usuario = request.user
            evaluacion_general.save()

            for categoria in categorias:
                for criterio in categoria.criterios.all():
                    puntaje = request.POST.get(f'criterio_{criterio.id}')
                    comentario = request.POST.get(f'comentario_{criterio.id}', '')  # Obtener el comentario
                    if puntaje:
                        Calificacion.objects.create(
                            evaluacion_general=evaluacion_general,
                            criterio=criterio,
                            puntaje=puntaje,
                            comentario=comentario  # Guardar el comentario
                        )

            return redirect('ver_evaluacion', evaluacion_id=evaluacion_general.id)

    else:
        evaluacion_general_form = EvaluacionGeneralForm()

    # Preparar descripciones de puntajes
    categorias_con_criterios = []
    for categoria in categorias:
        criterios_con_descripciones = []
        for criterio in categoria.criterios.all():
            descripciones_puntajes = {
                1: criterio.descripciones.filter(puntaje=1).first(),
                2: criterio.descripciones.filter(puntaje=2).first(),
                3: criterio.descripciones.filter(puntaje=3).first(),
                4: criterio.descripciones.filter(puntaje=4).first(),
                5: criterio.descripciones.filter(puntaje=5).first(),
            }
            criterios_con_descripciones.append({
                'criterio': criterio,
                'descripciones_puntajes': descripciones_puntajes,
            })
        categorias_con_criterios.append({
            'categoria': categoria,
            'criterios': criterios_con_descripciones,
        })

    context = {
        'rubrica': rubrica,
        'categorias': categorias_con_criterios,
        'evaluacion_general_form': evaluacion_general_form,
    }
    return render(request, 'rubricas/realizar_evaluacion.html', context)


def ver_evaluacion(request, evaluacion_id):
    evaluacion_general = get_object_or_404(EvaluacionGeneral, id=evaluacion_id)
    calificaciones = Calificacion.objects.filter(evaluacion_general=evaluacion_general).select_related('criterio')

    context = {
        'evaluacion_general': evaluacion_general,
        'calificaciones': calificaciones,
    }
    return render(request, 'rubricas/ver_evaluacion.html', context)