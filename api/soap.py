from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from django.views.decorators.csrf import csrf_exempt
from users.models import AuthToken, CustomUser
from django.contrib.auth import authenticate

class UserSoapService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Unicode)
    def authenticate_user(ctx, username, password):
        user = authenticate(username=username, password=password)
        if user:
            token = AuthToken.objects.create(user=user)
            return token.token
        return "Invalid credentials"

soap_app = Application(
    [UserSoapService],
    tns='news.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

django_soap_app = csrf_exempt(DjangoApplication(soap_app))