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


class AnnotationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    annotation = serializers.CharField(allow_blank=True, required=False)
    annotated_quote = serializers.CharField(max_length=255)
    annotated_quote_song = serializers.CharField(max_length=255)
    annotated_quote_image = serializers.CharField(allow_blank=True, required=False)
    annotated_quote_artist = serializers.CharField(max_length=255)
    annotated_quote_contrib = serializers.CharField(max_length=255)
    annotated_quote_id = serializers.IntegerField()
    annotated_quote_timestamp = serializers.CharField(max_length=255)
    annotator = serializers.CharField(max_length=255)
    annotation_view_count = serializers.IntegerField()
    last_viewed = serializers.CharField(max_length=255)
    upvotes = serializers.IntegerField()
    comments = serializers.ListField(child=serializers.DictField(), required=False)
    verified = serializers.BooleanField()

class QuotesSerializer(serializers.Serializer):
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



class QResponseSerializer(serializers.Serializer):
    timestamp = serializers.CharField(required=False)
    id = serializers.IntegerField()
    quote = serializers.CharField(max_length=255)
    image = serializers.CharField(max_length=255, allow_blank=True, required=False)
    song = serializers.CharField(max_length=255, allow_blank=True, required=False)
    contributor = serializers.CharField(max_length=255)
    artist = serializers.CharField(max_length=255)
    annotation = AnnotationSerializer()



