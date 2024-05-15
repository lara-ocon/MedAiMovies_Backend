from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):

    nombre = models.CharField(max_length=256)
    tel = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email


class Pelicula(models.Model):
    titulo = models.CharField(max_length=255)
    fecha_estreno = models.DateField()
    genero = models.CharField(max_length=50)
    duracion = models.IntegerField()
    pais = models.CharField(max_length=50)
    director = models.CharField(max_length=255)
    sinopsis = models.TextField()
    poster = models.URLField()
    nota = models.FloatField(null=True)
    # otros campos relevantes para una película

    def __str__(self):
        return self.titulo

class Review(models.Model):
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reseñas')
    # usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='reseñas') asi da otro error (solo se puede hacer una review por  usuario)
    usuario_email = models.EmailField()  # Agregado para almacenar el email del usuario
    calificacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario} - {self.pelicula}'
