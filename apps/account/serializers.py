from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirm')

    def validate(self, attrs):
        phone_number = attrs['phone_number'].strip()
        password_confirm = attrs.pop('password_confirm')
        password = attrs['password']
        if password != password_confirm:
            raise serializers.ValidationError('Password mismatch')
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError('Wrong password')
        if phone_number[0] != '+':
            attrs['phone_number'] = '+' + phone_number
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class RegisterCourierSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirm')

    def validate(self, attrs):
        phone_number = attrs['phone_number'].strip()
        password_confirm = attrs.pop('password_confirm')
        password = attrs['password']
        if password != password_confirm:
            raise serializers.ValidationError('Password mismatch')
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError('Wrong password')
        if phone_number[0] != '+':
            attrs['phone_number'] = '+' + phone_number
        return attrs

    def create(self, validated_data):
        user = User.objects.create_courier(**validated_data)
        return user


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=5, max_length=20, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('password', 'password_confirm')

    def validate(self, attrs):
        password_confirm = attrs.pop('password_confirm')
        password = attrs['password']
        if password != password_confirm:
            raise serializers.ValidationError('Password mismatch')
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError('Wrong password')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        data = {
            'id': repr['id'],
            'first_name': f"{repr['first_name']}",
            'last_name': f"{repr['last_name']}",
            'email': repr['email'],
            'phone_number': repr['phone_number'],
        }
        return data


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        data = {
            'first_name': f"{repr['first_name']}",
            'last_name': f"{repr['last_name']}",
            'email': repr['email'],
            'phone_number': repr['phone_number'],
        }
        return data


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", )




