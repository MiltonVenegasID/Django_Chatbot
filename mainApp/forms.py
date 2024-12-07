from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(required=True, label='Usuario', strip=False)
    email = forms.EmailField(required=True, label='Correo')
    first_name = forms.CharField(required=True,  label='Nombre')
    last_name = forms.CharField(required=True, label='Apellidos')
    phone_number = forms.IntegerField(required=True, label='Telefono')
    password1 = forms.CharField(required=True, label='Contraseña')
    password2 = forms.CharField(required=True, label='Confirmar Contraseña')
    user_type = forms.ChoiceField(choices=users_type.objects.values_list('id', 'NombreType'), label='Tipo de Usuario')    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name', 'user_type', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.UserType = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user

class TestRegister(forms.ModelForm):
    class Meta:
        model = key_user
        fields = ['Llave_asignada', 'Estado', 'Empresa_asignada', 'UsuarioRegistrado']
        
class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese OTP...'}),
        label="OTP"
    )
        
class CustomAuthenticationForm(AuthenticationForm):
    def  __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    Usuario = forms.CharField( widget=forms.TextInput(attrs={'id': 'usuariClass', 'label': 'Usuario'}))
    Contraseña = forms.CharField( widget=forms.PasswordInput(attrs={'id': 'usuariosClass', 'label': 'Contraseña'}))
    def set_request(self, request):
        self.request = request