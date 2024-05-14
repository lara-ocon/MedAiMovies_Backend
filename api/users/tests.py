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

    def test_login(self):
        data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data, "Token should be in response")
        self.assertIn("userId", response.data, "UserId should be in response")
        self.assertIn("session", response.cookies, "Session should be in response cookies")
        self.assertEqual(response.cookies['session']['samesite'], 'None', "Session cookie should have samesite=None")
        self.assertTrue(response.cookies['session']['secure'], "Session cookie should be secure")
        self.assertTrue(response.cookies['session']['httponly'], "Session cookie should be httponly")

    def test_login_wrong_password(self):
        data = {
            'email': 'test@gmail.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, 401)

class TestUsuarioView(TestCase):
    
    def test_usuario(self):
        data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data, "Password should not be in response")
        token = response.data['token']
        response = self.client.get('/api/users/me/', HTTP_COOKIE=f'session={token}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre'], 'prueba')
        self.assertEqual(response.data['tel'], '911')
        self.assertEqual(response.data['email'], 'prueba@gmail.com')
        self.assertNotIn("password", response.data, "Password should not be in response")
        self.assertNotIn("session", response.cookies, "Session should not be in response cookies")
        self.assertNotIn("userId", response.data, "UserId should not be in response")

class TestLogoutView(TestCase):
    
    def test_logout(self):
        data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'prueba@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 201)
        token = response.data['token']
        response = self.client.delete('/api/users/logout/', HTTP_COOKIE=f'session={token}')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/users/me/', HTTP_COOKIE=f'session={token}')
        self.assertEqual(response.status_code, 401)

class TestPeliculaCreateView(TestCase):
    
    def test_create_pelicula(self):
        data = {
            'titulo': 'prueba',
            'fecha_estreno': '2021-01-01',
            'genero': 'accion',
            'duracion': 120,
            'pais': 'Argentina',
            'director': 'Juan Perez',
            'sinopsis': 'Una pelicula de prueba',
            'poster': 'http://example.com/poster.jpg'
        }
        response = self.client.post('/api/peliculas/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['titulo'], 'prueba')
        self.assertEqual(response.data['fecha_estreno'], '2021-01-01')
        self.assertEqual(response.data['genero'], 'accion')
        self.assertEqual(response.data['duracion'], 120)
        self.assertEqual(response.data['pais'], 'Argentina')
        self.assertEqual(response.data['director'], 'Juan Perez')
        self.assertEqual(response.data['sinopsis'], 'Una pelicula de prueba')
        self.assertEqual(response.data['poster'], 'http://example.com/poster.jpg')
        self.assertNotIn("nota", response.data, "Nota should not be in response")

class TestPeliculaDetailView(TestCase):
        
    def test_pelicula_detail(self):
        data = {
            'titulo': 'prueba',
            'fecha_estreno': '2021-01-01',
            'genero': 'accion',
            'duracion': 120,
            'pais': 'Argentina',
            'director': 'Juan Perez',
            'sinopsis': 'Una pelicula de prueba',
            'poster': 'http://example.com/poster.jpg'
        }
        response = self.client.post('/api/peliculas/', data)
        self.assertEqual(response.status_code, 201)
        id = response.data['id']
        response = self.client.get(f'/api/peliculas/{id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['titulo'], 'prueba')
        self.assertEqual(response.data['fecha_estreno'], '2021-01-01')
        self.assertEqual(response.data['genero'], 'accion')
        self.assertEqual(response.data['duracion'], 120)
        self.assertEqual(response.data['pais'], 'Argentina')
        self.assertEqual(response.data['director'], 'Juan Perez')
        self.assertEqual(response.data['sinopsis'], 'Una pelicula de prueba')
        self.assertEqual(response.data['poster'], 'http://example.com/poster.jpg')
        self.assertEqual(response.data['nota'], 5)

class TestPeliculaSearchView(TestCase):
     
    def test_pelicula_search(self):
        data = {
            'titulo': 'prueba',
            'fecha_estreno': '2021-01-01',
            'genero': 'accion',
            'duracion': 120,
            'pais': 'Argentina',
            'director': 'Juan Perez',
            'sinopsis': 'Una pelicula de prueba',
            'poster': 'http://example.com/poster.jpg'
        }
        response = self.client.post('/api/peliculas/', data)
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/api/peliculas/search/?q=prueba&t=titulo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], 'prueba')
        self.assertEqual(response.data[0]['fecha_estreno'], '2021-01-01')
        self.assertEqual(response.data[0]['genero'], 'accion')
        self.assertEqual(response.data[0]['duracion'], 120)
        self.assertEqual(response.data[0]['pais'], 'Argentina')
        self.assertEqual(response.data[0]['director'], 'Juan Perez')
        self.assertEqual(response.data[0]['sinopsis'], 'Una pelicula de prueba')
        self.assertEqual(response.data[0]['poster'], 'http://example.com/poster.jpg')
        self.assertNotIn("nota", response.data[0], "Nota should not be in response")

        
class TestDeleteUsuarioView(TestCase):

    def test_delete_usuario(self):
        data = {
            'nombre': 'prueba',
            'tel': '911',
            'email': 'prueba@gmail.com'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 201)
        token = response.data['token']
        response = self.client.delete('/api/users/me/', HTTP_COOKIE=f'session={token}')
        self.assertEqual(response.status_code, 204)
        response = self.client.get('/api/users/me/', HTTP_COOKIE=f'session={token}')
        self.assertEqual(response.status_code, 401)

