import re
from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from api.users import models

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Usuario
        fields = ['id', 'nombre', 'tel', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def validate_tel(self, value):
            # Verifica que el numero de telefono tenga entre 7 y 9 digitos
            if re.match(r'^[0-9]{7,9}$', value):
                return value
            else:
                raise exceptions.ValidationError('Invalid phone number format')

    def validate_password(self, value):

        valid_password = re.match(r'^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z]).*$', value)
        if valid_password and len(value) >= 8:
            return value
        else:
            raise exceptions.ValidationError('Invalid password format')

    def create(self, validated_data):
        return models.Usuario.objects.create_user(username=validated_data['email'], **validated_data)

    def update(self, instance, validated_data):
        # Actualizamos solo los campos nombre y tel
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.save()
        return instance
        """Si quisiseramos actualizar la contraseña tambien, descomentar lo siguiente:
        if (validated_data.get('password')):
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
        """
    
class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):

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
        fields = ['id',
                  'titulo',
                  'fecha_estreno',
                  'genero',
                  'duracion',
                  'pais',
                  'director',
                  'sinopsis', 
                  'poster',
                  'nota'
        ]
        

class ReviewSerializer(serializers.ModelSerializer):
    # usuario_id = serializers.IntegerField(write_only=True) para que tambien se vea, se bueno tenerlo puesto por privacidad
    usuario_id = serializers.IntegerField(write_only=False)
    usuario_email = serializers.EmailField(read_only=True) # para q no se pueda escribir pero si leer

    class Meta:
        model = models.Review
        fields = ['id', 'usuario_id', 'usuario_email', 'pelicula', 'calificacion', 'comentario', 'fecha_creacion']
        read_only_fields = ['fecha_creacion', 'usuario_email']

    def validate_usuario_id(self, value):
        try:
            # Verifica que el usuario exista en la base de datos.
            models.Usuario.objects.get(pk=value)
            return value
        except models.Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado con este ID")

    def create(self, validated_data):
        # Asigna el usuario usando el ID proporcionado en el JSON de la solicitud.
        usuario_id = validated_data.pop('usuario_id')
        usuario = models.Usuario.objects.get(pk=usuario_id)
        validated_data['usuario'] = usuario
        validated_data['usuario_email'] = usuario.email

        # Actualizamos la nota de la película
        """
        pelicula = validated_data['pelicula']
        reviews = models.Review.objects.filter(pelicula=pelicula)
        nota = 0
        for review in reviews:
            nota += review.calificacion
        nota += validated_data['calificacion']
        pelicula.nota = nota / (len(reviews) + 1)
        pelicula.save()
        """

        return models.Review.objects.create(**validated_data)
