from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from api.users import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from .serializers import PeliculaSerializer, ReviewSerializer
from .models import Pelicula, Review
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class RegistroView(generics.CreateAPIView):

    serializer_class = serializers.UsuarioSerializer

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError) and 'email' in exc.detail and exc.detail['email'][0] == 'user with this email already exists.':
            exc.detail['email'][0] = "Ya existe un usuario registrado con ese email"
            return Response(exc.detail, status=status.HTTP_409_CONFLICT)
        return super().handle_exception(exc)


class LoginView(generics.CreateAPIView):

    serializer_class = serializers.LoginSerializer

    def post(self, request):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                token, created = Token.objects.get_or_create(user=serializer.validated_data)
                response = Response({'status': 'success', 'token': token.key, 'userId': token.user.id, 'email': token.user.email})
                response.set_cookie(key='session', value=token.key, samesite='None', httponly=True, secure=True) # secure = false para desarrollo
                return response
            else:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = serializers.UsuarioSerializer

    def get_object(self):
        # Obtiene el token del usuario desde la cookie en la solicitud
        token_key = self.request.COOKIES.get('session')
        if not token_key:
            raise NotFound('Session does not exist')
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            raise NotFound('Session does not exist')
        
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs) # metodo original de la clase
        if response.status_code == status.HTTP_204_NO_CONTENT:
            token_key = request.COOKIES.get('session')
            if token_key:
                try:
                    token = Token.objects.get(key=token_key)
                    token.delete()
                except Token.DoesNotExist:
                    pass
            response.delete_cookie('session', path='/', domain='medaimovies-backend.onrender.com', samesite='None')
        return response


@extend_schema(
    description='Logout endpoint',
    responses={
       204: OpenApiResponse(description='Logout successful'),
       401: OpenApiResponse(description='Invalid session'),
    }
)
class LogoutView(generics.DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        try:
            token_key = request.COOKIES.get('session')
            token = Token.objects.get(key=token_key)
            token.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.delete_cookie('session', path='/', domain='medaimovies-backend.onrender.com', samesite='None')
            return response
        except Token.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class PeliculaCreateView(generics.CreateAPIView):

    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PeliculaDetailView(generics.RetrieveUpdateDestroyAPIView):

    # Vista para ver, actualizar y eliminar peliculas
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Para actualizar la nota de forma dinamica
    def retrieve(self, request, *args, **kwargs):
        pelicula = self.get_object()
        reviews = Review.objects.filter(pelicula=pelicula)
        try:
            nota_media = round(reviews.aggregate(nota_media=Avg('calificacion'))['nota_media'], 2)
        except:
            nota_media = 5
        response_data = {
            'id': pelicula.id,
            'titulo': pelicula.titulo,
            'fecha_estreno': pelicula.fecha_estreno,
            'genero': pelicula.genero,
            'duracion': pelicula.duracion,
            'pais': pelicula.pais,
            'director': pelicula.director,
            'sinopsis': pelicula.sinopsis,
            'poster': pelicula.poster,
            'nota': nota_media
        }
        # cambiamos la nota de la pelicula
        pelicula.nota = nota_media
        pelicula.save()

        return Response(response_data)


@extend_schema(
    parameters=[
        OpenApiParameter(name='titulo', description='Filtrar por título de película', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='director', description='Filtrar por director', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='genero', description='Filtrar por género', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='sinopsis', description='Filtrar por sinopsis', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='nota', description='Filtrar por nota', required=False, type=OpenApiTypes.FLOAT),
    ]
)
class PeliculaSearchView(generics.ListAPIView):

    # Vista para buscar peliculas
    serializer_class = PeliculaSerializer

    def get_queryset(self):
        queryset = Pelicula.objects.all()
        # Obtenemos los queryparams
        titulo = self.request.query_params.get('titulo')
        director = self.request.query_params.get('director')
        genero = self.request.query_params.get('genero')
        sinopsis = self.request.query_params.get('sinopsis')
        nota = self.request.query_params.get('nota')

        # Hacemos un filtro en función de los queryparams recibidos
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
        if director:
            queryset = queryset.filter(director__icontains=director)
        if genero:
            queryset = queryset.filter(genero__icontains=genero)
        if sinopsis:
            queryset = queryset.filter(sinopsis__icontains=sinopsis)
        if nota:
            # Permitimos buscar redondeando, es decir con nota 3, nos valen pelis en el rango [3, 4)
            queryset = queryset.filter(nota__gte=float(nota), nota__lt=float(nota)+1)

        return queryset


class ReviewListCreateView(generics.ListCreateAPIView):
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # Para el POST
    def perform_create(self, serializer):
        serializer.save()

    # Para el GET
    def get_queryset(self):
        queryset = Review.objects.all()
        pelicula_id = self.request.query_params.get('pelicula', None)
        if pelicula_id is not None:
            queryset = queryset.filter(pelicula__id=pelicula_id)
        return queryset
