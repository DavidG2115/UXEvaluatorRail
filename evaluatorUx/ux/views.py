from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Import the messages module
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  # Import the AuthenticationForm and UserCreationForm
from django.contrib.auth import authenticate, login, logout  # Import the authenticate, login, and logout functions
from .forms import RubricaForm, EvaluacionGeneralForm, CalificacionForm  # Import the RubricaForm
from django.contrib.auth.decorators import login_required  # Import the login_required decorator
from .models import Criterio, Categoria, Rubrica, DescripcionPuntaje, Calificacion, EvaluacionGeneral  # Import the Rubrica and Categoria models
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    evaluaciones = EvaluacionGeneral.objects.filter(usuario=request.user).order_by('-fecha')
    rubricas = Rubrica.objects.filter(usuario=request.user)

    context = {
        'evaluaciones': evaluaciones,
        'rubricas': rubricas,
    }
    return render(request, 'rubricas/index.html', context)
@login_required
def crear_rubrica(request):
    rubrica_predefinida = Rubrica.objects.filter(predefinida=True).first()

    if request.method == "POST":
        if 'cargar_predefinida' in request.POST:
            # Cargar la rúbrica predefinida
            if rubrica_predefinida:
                rubrica = Rubrica.objects.create(
                    nombre=f'{rubrica_predefinida.nombre} (Copia)',
                    descripcion=rubrica_predefinida.descripcion,
                    usuario=request.user
                )

                for categoria in rubrica_predefinida.categorias.all():
                    nueva_categoria = Categoria.objects.create(
                        rubrica=rubrica,
                        nombre=categoria.nombre,
                        descripcion=categoria.descripcion
                    )

                    for criterio in categoria.criterios.all():
                        nuevo_criterio = Criterio.objects.create(
                            categoria=nueva_categoria,
                            nombre=criterio.nombre,
                            descripcion=criterio.descripcion
                        )

                        for descripcion_puntaje in criterio.descripciones.all():
                            DescripcionPuntaje.objects.create(
                                criterio=nuevo_criterio,
                                puntaje=descripcion_puntaje.puntaje,
                                descripcion=descripcion_puntaje.descripcion
                            )

                return redirect('editar_rubrica', rubrica_id=rubrica.id)

        else:
            # Crear una nueva rúbrica desde ce_
            nombre_rubrica = request.POST.get('nombre_rubrica')
            descripcion_rubrica = request.POST.get('descripcion_rubrica')

            rubrica = Rubrica.objects.create(nombre=nombre_rubrica, descripcion=descripcion_rubrica, usuario=request.user)

            # Obtener el número de categorías
            categorias_count = int(request.POST.get('categorias_count', 0))

            # Iterar sobre las categorías dinámicas
            for i in range(categorias_count):
                nombre_categoria = request.POST.get(f'categoria_{i}_nombre')
                descripcion_categoria = request.POST.get(f'categoria_{i}_descripcion')

                if nombre_categoria:  # Asegurarse de que el nombre no esté vacío
                    categoria = Categoria.objects.create(rubrica=rubrica, nombre=nombre_categoria, descripcion=descripcion_categoria)

                    # Obtener el número de criterios para esta categoría
                    criterios_count = int(request.POST.get(f'criterios_count_{i}', 0))

                    # Iterar sobre los criterios dinámicos
                    for j in range(criterios_count):
                        nombre_criterio = request.POST.get(f'criterio_{i}_{j}_nombre')
                        descripcion_criterio = request.POST.get(f'criterio_{i}_{j}_descripcion')

                        if nombre_criterio:  # Asegurarse de que el nombre del criterio no esté vacío
                            criterio = Criterio.objects.create(
                                categoria=categoria,
                                nombre=nombre_criterio,
                                descripcion=descripcion_criterio
                            )

                            # Crear las descripciones de los puntajes
                            for puntaje in range(1, 6):  # Puntajes del 1 al 5
                                descripcion_puntaje = request.POST.get(f'criterio_{i}_{j}_puntaje_{puntaje}')
                                if descripcion_puntaje:
                                    DescripcionPuntaje.objects.create(
                                        criterio=criterio,
                                        puntaje=puntaje,
                                        descripcion=descripcion_puntaje
                                    )

            return redirect('seleccionar_rubrica')  # Redirigir a una vista donde se liste las rúbricas

    return render(request, 'rubricas/crear.html', {'rubrica_predefinida': rubrica_predefinida})
@login_required
def seleccionar_rubrica(request):
    rubricas = Rubrica.objects.filter(usuario=request.user)
    
    if request.method == 'POST':
        rubrica_id = request.POST.get('rubrica_id')
        if rubrica_id:
            return redirect('editar_rubrica', rubrica_id=rubrica_id)
        else:
            messages.error(request, "Debes seleccionar una rúbrica.")

    return render(request, 'rubricas/seleccionar.html', {'rubricas': rubricas})

@login_required
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

@login_required
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

@login_required
def eliminar_rubrica(request, rubrica_id):
    rubrica = get_object_or_404(Rubrica, id=rubrica_id)
    rubrica.delete()
    return redirect('seleccionar_rubrica')



@login_required
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

@login_required
def ver_evaluacion(request, evaluacion_id):
    evaluacion_general = get_object_or_404(EvaluacionGeneral, id=evaluacion_id)
    calificaciones = Calificacion.objects.filter(evaluacion_general=evaluacion_general).select_related('criterio')

    # Preparar los datos para la gráfica
    labels = [calificacion.criterio.nombre for calificacion in calificaciones]
    data = [calificacion.puntaje for calificacion in calificaciones]

    context = {
        'evaluacion_general': evaluacion_general,
        'calificaciones': calificaciones,
        'labels': labels,
        'data': data,
    }
    return render(request, 'rubricas/ver_evaluacion.html', context)

@login_required
def eliminar_evaluacion(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionGeneral, id=evaluacion_id)
    if request.method == 'POST':
        evaluacion.delete()
        messages.success(request, 'La evaluación ha sido eliminada exitosamente.')
        return redirect('index')  
    return render(request, 'rubricas/ver_evaluacion.html', {'evaluacion_general': evaluacion})

def obtener_descripcion_promedio(promedio):
    if promedio <= 1:
        return "Muy Deficiente"
    elif promedio <= 2:
        return "Deficiente"
    elif promedio <= 3:
        return "Regular"
    elif promedio <= 4:
        return "Buena"
    else:
        return "Excelente"
    
@login_required
def generar_pdf(request, evaluacion_id):
    styles = getSampleStyleSheet()

    # Obtener la evaluación general y las calificaciones
    evaluacion_general = get_object_or_404(EvaluacionGeneral, id=evaluacion_id)
    calificaciones = Calificacion.objects.filter(evaluacion_general=evaluacion_general).select_related('criterio')

    # Crear un objeto HttpResponse con el tipo de contenido adecuado
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_evaluacion_{evaluacion_general.nombre_software}_{evaluacion_general.fecha.strftime("%d-%m-%Y")}.pdf"'

    # Crear un objeto canvas
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Agregar metadatos al PDF
    doc.title = f"Reporte de Evaluación - {evaluacion_general.nombre_software}"
    doc.author = request.user.username

    # Formatear la fecha
    fecha_formateada = evaluacion_general.fecha.strftime("%d-%m-%Y")

    # Agregar información de la evaluación al PDF
    elements.append(Paragraph(f"Evaluación de {evaluacion_general.nombre_software}", styles['Title']))
    elements.append(Paragraph(f"Realizada por: {evaluacion_general.usuario.username}", styles['Normal']))
    elements.append(Paragraph(f"Fecha: {fecha_formateada}", styles['Normal']))

    # Agregar categorías y calificaciones
    for categoria in evaluacion_general.rubrica.categorias.all():
        elements.append(Paragraph(f"Categoria: {categoria.nombre}", styles['Heading2']))

        # Crear la tabla de calificaciones
        data = [['Nombre del Criterio', 'Calificación', 'Comentario']]
        total_calificacion = 0
        count_calificaciones = 0

        for calificacion in calificaciones:
            if calificacion.criterio.categoria == categoria:
                data.append([
                    calificacion.criterio.nombre,
                    calificacion.get_puntaje_display(),
                    calificacion.comentario
                ])
                total_calificacion += calificacion.puntaje
                count_calificaciones += 1

        # Si no hay calificaciones, agregar un mensaje
        if len(data) == 1:
            data.append(['No hay calificaciones para esta categoría.', '', '', ''])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#02AC66')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black), 
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        # Alternar el color de fondo de las filas entre blanco y gris claro
        for i in range(1, len(data)):
            bg_color = colors.HexColor("#E0E0E0") if i % 2 == 0 else colors.white
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), bg_color),
            ]))
            
        elements.append(table)

        # Agregar un espacio entre la tabla y los textos de calificación total y promedio
        elements.append(Spacer(1, 12))

        # Agregar calificación total al final de la categoría
        if count_calificaciones > 0:
            promedio_calificacion = total_calificacion / count_calificaciones
            descripcion_promedio = obtener_descripcion_promedio(promedio_calificacion)
            elements.append(Paragraph(f"Calificación Total: {total_calificacion}", styles['Normal']))
            elements.append(Paragraph(f"Promedio de Calificación: {descripcion_promedio}", styles['Normal']))

        # Agregar un espacio después de cada categoría
        elements.append(Spacer(1, 24))
        
    # Crear la gráfica de barras
    drawing = Drawing(400, 200)
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 50
    bar_chart.height = 125
    bar_chart.width = 300
    bar_chart.data = [[calificacion.puntaje for calificacion in calificaciones]]
    bar_chart.categoryAxis.categoryNames = [calificacion.criterio.nombre for calificacion in calificaciones]
    bar_chart.bars[0].fillColor = colors.HexColor('#4BC0C0')

    # Rotar las etiquetas del eje X
    bar_chart.categoryAxis.labels.angle = 90
    bar_chart.categoryAxis.labels.dy = -10 
    bar_chart.categoryAxis.labels.boxAnchor = 'e'
    # Ajustar la posición vertical de las etiquetas

    drawing.add(bar_chart)
    elements.append(drawing)   

    # Construir el PDF
    doc.build(elements)

    return response