from django_soap.soap import soap_method, SoapView
from users.models import CustomUser, AuthToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer

class UserSoapService(SoapView):
    @soap_method
    def authenticate_user(self, username, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            token = AuthToken.objects.create(user=user)
            return {'token': token.token}
        return {'error': 'Invalid credentials'}
    
    @soap_method
    def list_users(self, token):
        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            if auth_token.user.is_admin():
                users = CustomUser.objects.all()
                return {'users': UserSerializer(users, many=True).data}
            return {'error': 'Unauthorized'}
        except AuthToken.DoesNotExist:
            return {'error': 'Invalid token'}
    
    @soap_method
    def create_user(self, token, user_data):
        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            if auth_token.user.is_admin():
                serializer = UserSerializer(data=user_data)
                if serializer.is_valid():
                    serializer.save()
                    return {'success': True, 'user': serializer.data}
                return {'error': 'Invalid data', 'details': serializer.errors}
            return {'error': 'Unauthorized'}
        except AuthToken.DoesNotExist:
            return {'error': 'Invalid token'}
    
    