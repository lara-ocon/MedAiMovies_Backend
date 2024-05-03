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


class RegistroView(generics.CreateAPIView):
    # TODO 13 y 15
    serializer_class = serializers.UsuarioSerializer

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError) and 'email' in exc.detail and exc.detail['email'][0] == 'user with this email already exists.':
            return Response(exc.detail, status=status.HTTP_409_CONFLICT)
        return super().handle_exception(exc)


class LoginView(generics.CreateAPIView):
    # TODO 16
    serializer_class = serializers.LoginSerializer

    def post(self, request):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                token, created = Token.objects.get_or_create(user=serializer.validated_data)
                print('login token:', token.key)
                print('login created:', created)
                response = Response({'status': 'success', 'token': token.key})

                # forma 1
                # response.set_cookie(key='session', value=token.key, secure=False, httponly=True, samesite='lax') # secure = false para desarrollo
                response.set_cookie(key='session', value=token.key, samesite='None', httponly=True, secure=True) # secure = false para desarrollo
                # response.set_cookie(key='session', value=token.key, samesite='lax')
                print('response.cookies:', response.cookies)

                # forma 2
                """
                if not created: # ESTO ANTES ERA IF NOT CREATED
                    response.set_cookie(key='session', value=token.key, secure=True,  samesite='lax')
                    print('response.cookies:', response.cookies)
                """
                print('response:', response)
                return response
            else:
                print('serializer.errors:', serializer.errors)
                return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(generics.RetrieveUpdateDestroyAPIView):
    # TODO 18 y 20
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


# TODO 26
@extend_schema(
    description='Logout endpoint',
    responses={
       204: OpenApiResponse(description='Logout successful'),
       401: OpenApiResponse(description='Invalid session'),
    }
)
class LogoutView(generics.DestroyAPIView):
    # TODO 19
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
    Vista para listar y crear peliculas
    """
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer


class PeliculaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para ver, actualizar y eliminar peliculas
    """
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer


# Para permitir las búsquedas por título y director
class PeliculaSearchView(generics.ListAPIView):
    serializer_class = PeliculaSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        tipo = self.request.query_params.get('t')
        if query:
            if tipo == "titulo":
                return Pelicula.objects.filter(Q(titulo__icontains=query))
            elif tipo == "director":
                return Pelicula.objects.filter(Q(director__icontains=query))
            elif tipo == "genero":
                return Pelicula.objects.filter(Q(genero__icontains=query))
            elif tipo == "sinopsis":
                return Pelicula.objects.filter(Q(sinopsis__icontains=query))
            elif tipo == "nota":
                # return Pelicula.objects.filter(Q(nota__icontains=query))
                print("Falta añadir la nota al modelo")
        return Pelicula.objects.all()


class ReviewListCreateView(generics.ListCreateAPIView):
    # forma 1:
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    """

    # forma 2:
    '''
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Permite que los usuarios no autenticados puedan ver las reseñas
    print('hoola')
    def get_queryset(self):
        """
        Este método sobrescrito permite filtrar las reseñas por la película.
        """
        print('cookies en review backend:', self.request.COOKIES)
        print('cookies')
        pelicula_id = self.request.query_params.get('pelicula')
        if pelicula_id is not None:
            return Review.objects.filter(pelicula=pelicula_id)
        return Review.objects.none()  # Retorna vacío si no hay un parámetro 'pelicula'
    '''

    # forma 3:
    # check headers of request
    """
    def get_queryset(self):
        print('cookies en review backend:', self.request.COOKIES)
        print('headers en review backend:', self.request.headers)
        print('headers en review backend:', self.request.headers.get('Authorization'))
        print('headers en review backend:', self.request.headers.get('Cookie'))
        print('headers en review backend:', self.request.headers.get('cookie'))
        pelicula_id = self.request.query_params.get('pelicula')
        if pelicula_id is not None:
            return Review.objects.filter(pelicula=pelicula_id)
        return Review.objects.all()
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        try:
            token = Token.objects.get(key=self.request.COOKIES.get('session'))
            print('token:', token)
            serializer.save(usuario=token.user)
        except Token.DoesNotExist:
            print('raise ValidationError')
            raise ValidationError('No se ha iniciado sesión')

    def get_queryset(self):
        print('cookies en review backend:', self.request.headers)
        pelicula_id = self.request.query_params.get('pelicula')
        if pelicula_id is not None:
            return Review.objects.filter(pelicula=pelicula_id)
        return Review.objects.all()
