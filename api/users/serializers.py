import re
from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from api.users import models

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        # TODO: 5 y 22
        model = models.Usuario
        fields = ['nombre', 'tel', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def validate_password(self, value):
        # TODO: 7: completar
        valid_password = re.match(r'^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$', value)
        if valid_password and len(value) >= 8:
            return value
        else:
            raise exceptions.ValidationError('Invalid password format')

# TODO: 8
    def create(self, validated_data):
        return models.Usuario.objects.create_user(username=validated_data['email'], **validated_data)

    def update(self, instance, validated_data):
        if (validated_data.get('password')):
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
    
class LoginSerializer(serializers.Serializer):
    # TODO: 10
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        # TODO: 11

        email = data['email']
        password = data['password']

        user = authenticate(username=email, password=password)

        if user:
            return user
        else:
            raise exceptions.AuthenticationFailed('Invalid credentials')


class PeliculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pelicula
        fields = ['titulo',
                  'fecha_estreno',
                  'genero',
                  'duracion',
                  'pais',
                  'director',
                  'sinopsis',
                  'poster']
        