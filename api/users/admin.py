from django.contrib import admin
from api.users import models


admin.site.register(models.Usuario)
admin.site.register(models.Pelicula)
admin.site.register(models.Review)
