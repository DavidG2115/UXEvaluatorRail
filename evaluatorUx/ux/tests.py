from django.test import TestCase, Client
from django.urls import reverse
from .models import Rubrica, Categoria, Criterio, DescripcionPuntaje
from django.contrib.auth.models import User

class EditarRubricaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        
        self.rubrica = Rubrica.objects.create(nombre='Rubrica 1', descripcion='Descripcion 1', usuario=self.user)
        self.categoria = Categoria.objects.create(rubrica=self.rubrica, nombre='Categoria 1', descripcion='Descripcion Categoria 1')
        self.criterio = Criterio.objects.create(categoria=self.categoria, nombre='Criterio 1', descripcion='Descripcion Criterio 1')
        for puntaje in range(1, 6):
            DescripcionPuntaje.objects.create(criterio=self.criterio, puntaje=puntaje, descripcion=f'Descripcion Puntaje {puntaje}')

    def test_editar_rubrica(self):
        url = reverse('editar_rubrica', args=[self.rubrica.id])
        data = {
            'nombre': 'Rubrica Editada',
            'descripcion': 'Descripcion Editada',
            f'categoria_nombre_{self.categoria.id}': 'Categoria Editada',
            f'categoria_descripcion_{self.categoria.id}': 'Descripcion Categoria Editada',
            f'criterio_nombre_{self.criterio.id}': 'Criterio Editado',
            f'criterio_descripcion_{self.criterio.id}': 'Descripcion Criterio Editado',
        }
        for puntaje in range(1, 6):
            data[f'descripcion_puntaje_{self.criterio.id}_{puntaje}'] = f'Descripcion Puntaje Editada {puntaje}'

        response = self.client.post(url, data)
        
        self.rubrica.refresh_from_db()
        self.categoria.refresh_from_db()
        self.criterio.refresh_from_db()
        
        self.assertEqual(self.rubrica.nombre, 'Rubrica Editada')
        self.assertEqual(self.rubrica.descripcion, 'Descripcion Editada')
        self.assertEqual(self.categoria.nombre, 'Categoria Editada')
        self.assertEqual(self.categoria.descripcion, 'Descripcion Categoria Editada')
        self.assertEqual(self.criterio.nombre, 'Criterio Editado')
        self.assertEqual(self.criterio.descripcion, 'Descripcion Criterio Editado')
        
        for puntaje in range(1, 6):
            descripcion_puntaje = DescripcionPuntaje.objects.get(criterio=self.criterio, puntaje=puntaje)
            self.assertEqual(descripcion_puntaje.descripcion, f'Descripcion Puntaje Editada {puntaje}')
        
        self.assertRedirects(response, reverse('ver_rubrica', args=[self.rubrica.id]))