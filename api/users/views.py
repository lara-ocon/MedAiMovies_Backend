from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.utils import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from api.users import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth import authenticate
from .serializers import PeliculaSerializer, ReviewSerializer
from .models import Pelicula, Review
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
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
                print('login token:', token.key)
                print('login created:', created)
                response = Response({'status': 'success', 'token': token.key, 'userId': token.user.id, 'email': token.user.email})

                # forma 1
                # response.set_cookie(key='session', value=token.key, secure=False, httponly=True, samesite='lax') # secure = false para desarrollo
                response.set_cookie(key='session', value=token.key, samesite='None', httponly=True, secure=True) # secure = false para desarrollo
                # response.set_cookie(key='session', value=token.key, samesite='lax')
                print('response.cookies:', response.cookies)

                # forma 2
                """
                if not created: # ESTO ANTES ERA IF NOT CREATED
                    response.set_cookie(key='session', value=token.key, secure=True,  samesite='lax')
                    print('response.cookies:', response.cookies)
                """
                print('response:', response)
                return response
            else:
                print('serializer.errors:', serializer.errors)
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = serializers.UsuarioSerializer

    def get_object(self):
        # Obtiene el token del usuario desde la cookie en la solicitud
        token_key = self.request.COOKIES.get('session')
        print('token_key:', token_key)
        print('cookies en usuario view:', self.request.COOKIES)
        if not token_key:
            print('raise NotFound')
            raise NotFound('Session does not exist')
        try:
            token = Token.objects.get(key=token_key)
            print('token:', token)
            print('token.user:', token.user)
            return token.user
        except Token.DoesNotExist:
            print('raise NotFound 2')
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
            response.delete_cookie('session', path='/', domain='127.0.0.1', samesite='None')
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
            print('token_key to delete:', token_key)
            token = Token.objects.get(key=token_key)
            token.delete()
            response = Response(status=status.HTTP_204_NO_CONTENT)
            print('cookie de session antes de borrar:', response.cookies)
            # response.delete_cookie('session')
            response.delete_cookie('session', path='/', domain='127.0.0.1', samesite='None')
            print('se ha borrado la cookie de session')
            return response
        except Token.DoesNotExist:
            print('no existe token a borrar')
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class PeliculaCreateView(generics.CreateAPIView):
    """
    Vista para crear peliculas
    """
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # para el metodo get
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PeliculaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para ver, actualizar y eliminar peliculas
    """
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Para actualizar la nota de forma dinamica
    def retrieve(self, request, *args, **kwargs):
        pelicula = self.get_object()
        reviews = Review.objects.filter(pelicula=pelicula)
        nota_media = reviews.aggregate(nota_media=Avg('calificacion'))['nota_media'] or 5
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
    """
    Vista para buscar peliculas
    """

    serializer_class = PeliculaSerializer

    def get_queryset(self):
        queryset = Pelicula.objects.all()
        # Retrieve all relevant query parameters
        titulo = self.request.query_params.get('titulo')
        director = self.request.query_params.get('director')
        genero = self.request.query_params.get('genero')
        sinopsis = self.request.query_params.get('sinopsis')
        nota = self.request.query_params.get('nota')

        # Filter based on each parameter if it's provided
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)
        if director:
            queryset = queryset.filter(director__icontains=director)
        if genero:
            queryset = queryset.filter(genero__icontains=genero)
        if sinopsis:
            queryset = queryset.filter(sinopsis__icontains=sinopsis)
        if nota:
            # permitimos buscar redondeando, es decir si buscamos
            # notas de 3, nos valgan pelis en el rango [3, 4)
            queryset = queryset.filter(nota__gte=float(nota), nota__lt=float(nota)+1)

        return queryset


class ReviewListCreateView(generics.ListCreateAPIView):
    
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # when POST request is made
    def perform_create(self, serializer):
        serializer.save()

    # when GET request is made
    def get_queryset(self):
        queryset = Review.objects.all()
        pelicula_id = self.request.query_params.get('pelicula', None)
        print('pelicula_id:', pelicula_id)
        if pelicula_id is not None:
            queryset = queryset.filter(pelicula__id=pelicula_id)
        return queryset
