from rest_framework.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from api.users import serializers

class TestUsuarioSerializer(SimpleTestCase):
    
    def test_validate_password(self):

        correct_password = 'Aa345678'
        self.assertEqual(serializers.UsuarioSerializer().validate_password(correct_password), correct_password)

        wrong_password = '12345678' # No contiene letras
        with self.assertRaises(ValidationError):
            serializers.UsuarioSerializer().validate_password(wrong_password)


class TestRegistroView(TestCase):
    
    def test_registro(self):
        data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data, "Password should not be in response")

class TestLoginView(TestCase):
    def test_login_success(self):
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        register_data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

class TestUsuarioView(TestCase):
    def test_usuario_view_get(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.client.cookies = response.cookies
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@gmail.com')

    def test_usuario_view_actualizar(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.client.cookies = response.cookies
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@gmail.com')
        #modify user
        id = response.data['id']
        email = response.data['email']
        data = {
            'id': id,
            'nombre': 'prueba2',
            'tel': '911',
            'email': email
        }
        response = self.client.put('/api/users/me/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre'], 'prueba2')
        self.assertEqual(response.data['tel'], '911')
    
    def test_usuario_view_delete(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.client.cookies = response.cookies
        response = self.client.delete('/api/users/me/')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 404)

class TestLogoutView(TestCase):
    def test_logout(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        }
        user_data = {
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.client.cookies = response.cookies
        response = self.client.delete('/api/users/logout/')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 404)

class TestPeliculaCreateView(TestCase):
    def test_pelicula_create(self):
        user_data = {
            'email': 'admin@email.com',
            'password': 'Contrasenia123'
        }
        response = self.client.post('/admin/', user_data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/peliculas/', {
            'titulo': 'Pelicula 1',
            'fecha_estreno': '2021-10-10',
            'genero': 'Accion',
            'duracion': 120,
            'pais': 'Argentina',
            'director': 'Director 1',
            'sinopsis': 'Sinopsis de la pelicula 1',
            'poster': 'https://www.google.com',
            'nota': 5
        })
        self.assertEqual(response.status_code, 201)

class TestPeliculaDetailView(TestCase):
    def test_pelicula_detail(self):
        user_data = {
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        })
        response = self.client.post('/api/users/login/', user_data)
        self.client.cookies = response.cookies
        response = self.client.get('/api/peliculas/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)