from rest_framework import serializers
from accounts.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
 




class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
          'external_id',
          'username',
          'email',
          'id_membre_association',
          'first_name',
          'last_name',
          'role'
        ]

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserMeSerializer()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # utilisateur connecté
        user = self.user

        # serializer user existant
        user_data = UserMeSerializer(user).data

        # réponse custom
        return {
            "access": data["access"],
            "refresh": data["refresh"],
            "user": user_data,
            "role": user.role,
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)


    class Meta:
        model = User
        fields = ( 'first_name', 'last_name','password', 'email')

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role='CLIENT'
        )
        return user
    
class RegisterResponseSerializer(serializers.Serializer):
    status_code = serializers.IntegerField()
    message = serializers.CharField()
    user = UserMeSerializer()