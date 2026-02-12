from rest_framework import serializers
from accounts.models import User




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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)


    class Meta:
        model = User
        fields = ( 'first_name', 'last_name','password', 'email')

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,   
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role='CLIENT'
        )
        return user
    
