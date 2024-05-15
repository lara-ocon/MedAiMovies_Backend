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
    
    def test_validate_tel(self):
            
        correct_tel = '911123456'
        self.assertEqual(serializers.UsuarioSerializer().validate_tel(correct_tel), correct_tel)

        wrong_tel = '123456'
        with self.assertRaises(ValidationError):
            serializers.UsuarioSerializer().validate_tel(wrong_tel)

        wrong_tel = '1234567890'
        with self.assertRaises(ValidationError):
            serializers.UsuarioSerializer().validate_tel(wrong_tel)


class TestRegistroView(TestCase):
    
    def test_registro(self):
        data = {
            'nombre': 'prueba',
            'tel': '911123456',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data, "Password should not be in response")
    
    def test_registro_fail(self):
        data = {
            'nombre': 'prueba',
            'tel': '911123456',
            'email': 'test',
            'password': 'Aa345678'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, 400)

class TestLoginView(TestCase):
    def test_login_success(self):
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
    
    def test_login_fail(self):
        user_data = {
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
            'email': 'test@gmail.com',
            'password': 'malacontraseña'
        }
        self.client.post('/api/users/', register_data)
        response = self.client.post('/api/users/login/', user_data)
        self.assertEqual(response.status_code, 403)

class TestUsuarioView(TestCase):
    def test_usuario_view_get(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
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

    def test_usuario_view_get_fail(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 404)

    def test_usuario_view_actualizar(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
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
        data = {
            'nombre': 'prueba2',
            'tel': '911234567',
            'email': 'test@gmail.com',
            'password': 'Aa345678'
        }
        response = self.client.put('/api/users/me/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre'], 'prueba2')
        self.assertEqual(response.data['tel'], '911234567')
    
    def test_usuario_view_delete(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
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
    
    def test_usuario_view_delete_fail(self):
        response = self.client.delete('/api/users/me/')
        self.assertEqual(response.status_code, 404)

class TestLogoutView(TestCase):
    def test_logout(self):
        register_data = {
            'nombre': 'prueba',
            'tel': '911123456',
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
    
    def test_logout_fail(self):
        response = self.client.delete('/api/users/logout/')
        self.assertEqual(response.status_code, 401)
