from rest_framework.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from api.users import serializers

class TestUsuarioSerializer(SimpleTestCase):
    # TODO: 21
    
    def test_validate_password(self):

        correct_password = 'Aa345678'
        self.assertEqual(serializers.UsuarioSerializer().validate_password(correct_password), correct_password)

        wrong_password = '12345678' # No contiene letras
        with self.assertRaises(ValidationError):
            serializers.UsuarioSerializer().validate_password(wrong_password)


class TestRegistroView(TestCase):
    # TODO: 22
    
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
