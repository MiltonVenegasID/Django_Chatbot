from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only = True)
    isAdmin = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = User
        fields= ['id', 'first_name','email', 'name', 'isAdmin']
    
    def get_isAdmin(self, obj):
        return obj.is_staff
    
    def get_name(self, obj):
          name = obj.first_name
          if name == '':
              name = obj.email
          return name 

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model=User
        fields = ['id', 'username', 'email', 'name', 'isAdmin', 'token']
        
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
        