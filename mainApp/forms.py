from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(required=True, label='Usuario', strip=False, widget=forms.TextInput(attrs={'aria-label': 'Usuario', 'class': 'form-control'}))
    email = forms.EmailField(required=True, label='Correo', widget=forms.EmailInput(attrs={'aria-label': 'Correo', 'class': 'form-control'}))
    first_name = forms.CharField(required=True, label='Nombre', widget=forms.TextInput(attrs={'aria-label': 'Nombre', 'class': 'form-control'}))
    last_name = forms.CharField(required=True, label='Apellidos', widget=forms.TextInput(attrs={'aria-label': 'Apellidos', 'class': 'form-control'}))
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': '', 'aria-label': 'Telefono', 'class': 'form-control'}), label=("Telefono"), required=True)
    password1 = forms.CharField(
     label="Contraseña",
     strip=False,
     widget=forms.PasswordInput
    )
    password2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirmar Contraseña')
    user_type = forms.ModelChoiceField(
        queryset=users_type.objects.all(),
        label='Tipo de Usuario',
        to_field_name='id',
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
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