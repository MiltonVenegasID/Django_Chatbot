from django.urls import path, include
from mainApp.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('Logout', LogoutView.as_view(), name="logout"),
    path('', Inicio.as_view(authentication_form = CustomAuthenticationForm), name="index"),
    path('ruleOTP', OTPView.as_view(), name="ruleOTP"),
    path('Iris', Iris.as_view(), name="Iris"),
    path('Conversacion', get_bot_response,name ="Comm"),
    path('borrarIris', borrarIris, name="borrarConocimiento"),
    path('RegistroVista', VistaRegistro.as_view(), name='Registro'),
    path('Test', Med.as_view(), name=  'Test'),
    path('CreateSubAccount', CreateSubAccount, name='CreateSubAccount'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)