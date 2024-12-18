from django.db import models
from django.conf import  settings
from encrypted_model_fields.fields import EncryptedCharField
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField


class users_type(models.Model):
    NombreType = models.CharField(max_length=50)

    def __str__(self):
        return self.NombreType

class CustomUser(AbstractUser):
    UserType = models.ForeignKey(users_type, on_delete=models.CASCADE, null=True)
    phone_number = PhoneNumberField(blank=True)
    address = models.TextField(max_length=50, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=3)
    otp_max_out = models.DateTimeField(blank=True, null=True)

class Choice(models.Model):
    PruebaTexto = models.CharField(max_length=200)
    ValoresEnteros = models.IntegerField(default=0)
    
class DireccionImei(models.Model):
    Nombre = models.CharField(max_length=255)
    Imei = models.IntegerField(default=0)
    FechaObtencion = models.DateField()
    Usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class empresas(models.Model):
    Nombre = models.CharField(max_length=150)

class key_user(models.Model):
    UsuarioRegistrado = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    Empresa_asignada= models.ForeignKey(empresas, on_delete = models.CASCADE)
    Llave_asignada = EncryptedCharField(max_length = 255)
    Estado = models.PositiveSmallIntegerField()
    Fecha_creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [["UsuarioRegistrado", "Empresa_asignada"]]

class equipos(models.Model):
    Nombre = models.CharField(max_length=250)
    Imei = models.IntegerField(default = 0)
    Empresa = models.ForeignKey(empresas, on_delete=models.CASCADE)
    Fecha_Ingreso = models.DateTimeField(auto_now_add = True)
    Usuario = models.ForeignKey(CustomUser, on_delete = models.CASCADE, null=True)