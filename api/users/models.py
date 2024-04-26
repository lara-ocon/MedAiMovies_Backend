from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    # TODO: 2

    nombre = models.CharField(max_length=256)
    tel = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Pelicula(models.Model):
    titulo = models.CharField(max_length=255)
    fecha_estreno = models.DateField()
    genero = models.CharField(max_length=50)
    duracion = models.IntegerField()
    pais = models.CharField(max_length=50)
    director = models.CharField(max_length=255)
    sinopsis = models.TextField()
    poster = models.URLField()
    # otros campos relevantes para una película

class Review(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reseñas')
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name='reseñas')
    calificacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)