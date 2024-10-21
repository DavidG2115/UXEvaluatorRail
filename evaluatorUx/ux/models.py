from django.db import models
from django.contrib.auth.models import User

# Modelo Rubrica
class Rubrica(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rubricas')

    def __str__(self):
        return self.nombre

# Modelo Categoria
class Categoria(models.Model):
    rubrica = models.ForeignKey(Rubrica, related_name='categorias', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# Modelo Criterio
class Criterio(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='criterios', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
    # Nuevo método para obtener la descripción de un puntaje
    def get_descripcion_puntaje(self, puntaje):
        try:
            return self.descripciones.get(puntaje=puntaje).descripcion
        except DescripcionPuntaje.DoesNotExist:
            return "Descripción no disponible para este puntaje"

# Modelo DescripcionPuntaje (para almacenar descripciones de los puntajes 1-5)
class DescripcionPuntaje(models.Model):
    criterio = models.ForeignKey(Criterio, related_name='descripciones', on_delete=models.CASCADE)
    puntaje = models.IntegerField(choices=[(1, 'Muy Deficiente'), (2, 'Deficiente'), (3, 'Aceptable'), (4, 'Buena'), (5, 'Excelente')])
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.criterio.nombre} - {self.get_puntaje_display()}"

# Modelo Evaluacion
class Evaluacion(models.Model):
    rubrica = models.ForeignKey(Rubrica, related_name='evaluaciones', on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    criterio = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    puntaje = models.IntegerField(choices=[(1, 'Muy Deficiente'), (2, 'Deficiente'), (3, 'Aceptable'), (4, 'Buena'), (5, 'Excelente')])
    comentario = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones')

    def __str__(self):
        return f"Evaluación - {self.rubrica.nombre} - {self.categoria.nombre} - {self.criterio.nombre}"
