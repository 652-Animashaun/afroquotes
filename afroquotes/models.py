from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime    
from djrichtextfield.models import RichTextField
from djongo import models as mongo_models
import random 

# Create your models here.
default_usernames= ["Amina1","Kwame4","Imani7","Sade92","Jelani5","Fatou3","Chuma8","NiaBee","Tafari","ZolaK9"]
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # def create_superuser(self, email, password, **extra_fields):
    #     user = self.create_user(
    #             email=self.normalize_email(email),
    #         )
    #     user.is_admin = True
    #     user.is_staff = True
    #     user.is_superuser = True
    #     user.set_password(password)
    #     user.save(using=self._db)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=20, default=random.choice(default_usernames))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    bio = models.CharField(max_length=256, null=True)
    profile_image= models.URLField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_annotation_iq(self):
        contributed_annotation = Annotation.objects.filter(annotator=self)
        annotation_iq=0
        if contributed_annotation:

          for annotation in contributed_annotation:
              upvote_count = annotation.get_upvotes()
              annotation_iq += upvote_count
        return annotation_iq

    def get_annotations(self):
        return Annotation.objects.filter(annotator=self).values("annotated")


class Quote(models.Model):
    quote=models.CharField(max_length=500)
    artist=models.CharField(max_length=64)
    song=models.CharField(max_length=64, null=True)
    image= models.URLField()
    contributor= models.ForeignKey(User, on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    # approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quote} {self.song} {self.artist}"

    def serialize(self):
        return{
            "id": self.id,
            "quote":self.quote,
            "image":self.image,
            "song": self.song,
            "contributor":self.contributor.username,
            "artist":self.artist,
            "date":self.timestamp.strftime("%A, %d. %B %d/%m/%Y %I:%M%p"),
            "annotation":self.quote_annotation()
        }

    def quote_annotation(self):
        annotation = Annotation.objects.filter(annotated=self)
        if annotation:
            return annotation[0].serialize()
        else:
            return None

    
class Annotation(models.Model):
    annotation=models.CharField(max_length=300)
    annotator=models.ForeignKey(User, on_delete=models.DO_NOTHING)
    annotated=models.ForeignKey(Quote, on_delete=models.DO_NOTHING)
    verified= models.BooleanField(default=False)
    annotation_view_count=models.IntegerField(null=True, default=0)
    last_viewed=models.DateTimeField(null=True)
    timestamp = models.DateTimeField(default=datetime.now)
    approvers = models.ManyToManyField(User, related_name="approvers")

    def serialize(self):
        return{
            "id":self.id,
            "annotation":self.annotation,
            "annotated_quote": self.annotated.quote,
            "annotated_quote_song": self.annotated.song,
            "annotated_quote_image": self.annotated.image,
            "annotated_quote_artist": self.annotated.artist,
            "annotated_quote_contrib": self.annotated.contributor.username,
            "annotated_quote_id": self.annotated.id,
            "annotated_quote_timestamp": self.annotated.timestamp.strftime("%A, %d. %B %d/%m/%Y %I:%M%p"),
            "annotator": self.annotator.username,
            "annotation_view_count":self.annotation_view_count,
            "last_viewed":self.last_viewed.strftime("%A, %d. %B %d/%m/%Y %I:%M%p") if self.last_viewed else None,
            "upvotes": self.upvotes.count() if self.upvotes else 0,
            "comments": self.get_comments(),
            "verified":self.verified,
        }


    def check_veracity(self):
        if self.approvers.count() >= 2 and self.annotator not in [approver for approver in self.approvers.all()]:
            self.verified = True
            self.save()

    def get_upvotes(self):
        return self.upvotes.count() 
    def get_user_upvote(self, user_id):
        return True if Upvote.objects.filter(user=user_id, annotation=self.id) else False
    def get_comments(self):
        comments= SuggestionComment.objects.filter(annotation=self)
        return [comment.serialize() for comment in comments]


class Upvote(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name="upvotes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvoted")
    timestamp = models.DateTimeField(auto_now_add=True)

class SuggestionComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_suggestion")
    annotation= models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name="comments")
    suggestion = models.CharField(max_length=300)

    def serialize(self):
        return{

        "id": self.id,
        "user": self.user.username,
        # "annotation": self.annotation.serialize(),
        "annotation_id": self.annotation.id,
        "suggestion": self.suggestion

        }


