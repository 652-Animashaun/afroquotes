from rest_framework import serializers
from .models import User, Quote, Annotation
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,
                                     style={'input_type': 'password'})
    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        write_only_fields = ('password')
        read_only_fields = ('is_staff', 'is_superuser', 'is_active')

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': ('Email is already in use')})

        return super().validate(attrs)

    def create(self, validated_data):
        try:
            user = super(CreateUserSerializer, self).create(validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user
        except IntegrityError as ex:
            raise ValueError(ex)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'bio', 'profile_image')

class AnnotationSerializer (serializers.ModelSerializer):
    quote = serializers.CharField()
    artist = serializers.CharField()
    song = serializers.CharField()
    image = serializers.URLField()
    contributor = serializers.IntegerField(required=False)
    annotation = serializers.CharField()

    class Meta:
        model = Annotation
        fields = ('quote', 'artist', 'song', 'image', 'contributor')

class QuotesSerializer(serializers.ModelSerializer):
    quote = serializers.CharField()
    artist = serializers.CharField()
    song = serializers.CharField()
    image = serializers.URLField()
    contributor = serializers.IntegerField(required=False)

    class Meta:
        model = Quote
        fields = ('quote', 'artist', 'song', 'image', 'contributor')

class UserProfile(serializers.Serializer):
    pass


