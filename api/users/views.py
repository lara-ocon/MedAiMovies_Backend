from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from api.users import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth import authenticate




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
                response = Response({'status': 'success'})

                # forma 1
                # response.set_cookie(key='session', value=token.key, secure=False, httponly=True, samesite='lax') # secure = false para desarrollo
                response.set_cookie(key='session', value=token.key, samesite='None', secure=True) # secure = false para desarrollo
                print('response.cookies:', response.cookies)

                # forma 2
                """
                if not created: # ESTO ANTES ERA IF NOT CREATED
                    response.set_cookie(key='session', value=token.key, secure=True, httponly=True, samesite='lax')
                    print('response.cookies:', response.cookies)
                """
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
        print('cookies:', self.request.COOKIES)
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
            response.delete_cookie('session')
            return response
        except Token.DoesNotExist:
            print('no existe token a borrar')
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
# version Miguel
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from api.users import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.http import Http404


class RegistroView(generics.CreateAPIView):
    # TODO: 13 y 15

    serializer_class = serializers.UsuarioSerializer 

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response(exc.detail, status=status.HTTP_409_CONFLICT)
        else:
            return super().handle_exception(exc)


class LoginView(generics.CreateAPIView):
    # TODO: 16
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, created = Token.objects.get_or_create(user=user)
            response = Response({'status': 'success'})
            print('token en login', token)
            print('created', created)
            if not created:
                response.set_cookie(key='session', value=token.key, secure=True, httponly=True, samesite='lax')
                print('cookie', response.cookies)
            return response
        else:
            print('serializer.errors', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UsuarioSerializer

    def get_object(self):
        session_key = self.request.COOKIES.get('session')
        print('session_key', session_key)
        print('self.request.COOKIES', self.request.COOKIES)
        if not session_key:
            print('No session token provided')
            raise Http404("No session token provided")

        try:
            user = Token.objects.get(key=session_key).user
            print('user', user)
            return user
        except Token.DoesNotExist:
            print('No user found for given session token')
            raise Http404("No user found for given session token")


# TODO: 26
@extend_schema(
    description='Logout endpoint',
    responses={
    204: OpenApiResponse(description='Logout successful'),
    401: OpenApiResponse(description='Invalid session')
    }
)
class LogoutView(generics.DestroyAPIView):
    # TODO: 19

    # def delete(self, request):
    #     response = Response({"status": "success"})
    #     Token.objects.get(key=request.COOKIES.get('session'))
    #     response.delete_cookie('session') 
    #     return response
    
    # TODO: 20
    
    def delete(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT, data={"status": "success"})
        try:
            if Token.objects.get(key=request.COOKIES.get('session')):
                response.delete_cookie('session')
                return response
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"error": "Invalid session"})
"""