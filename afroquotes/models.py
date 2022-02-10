from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime    
from djrichtextfield.models import RichTextField

# Create your models here.

class User(AbstractUser):
	pass

class Quote(models.Model):
	quote=models.CharField(max_length=500)
	artist=models.CharField(max_length=64)
	song=models.CharField(max_length=64, null=True)
	image= models.URLField()
	contributor= models.ForeignKey(User, on_delete=models.DO_NOTHING)
	timestamp = models.DateTimeField(auto_now_add=True, null=True)

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
			"date":self.timestamp.strftime("%A, %d. %B %d/%m/%Y %I:%M%p")
		}
	
class Annotation(models.Model):
	annotation=models.CharField(max_length=300)
	annotator=models.ForeignKey(User, on_delete=models.DO_NOTHING)
	annotated=models.ForeignKey(Quote, on_delete=models.DO_NOTHING)
	verified= models.BooleanField(default=False)
	annotation_view_count=models.IntegerField(null=True, default=0)
	last_viewed=models.DateTimeField(null=True)
	timestamp = models.DateTimeField(default=datetime.now)


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
			"annotated_quote_timestamp": self.annotated.timestamp,
			"annotator": self.annotator.username,
			"annotation_view_count":self.annotation_view_count,
			"last_viewed":self.last_viewed,
			"upvotes": self.upvotes.count() 
		}

	def get_upvotes(self):
		return self.upvotes.count() 



class Upvote(models.Model):
	annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name="upvotes")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvoted")
	timestamp = models.DateTimeField(auto_now_add=True)

class SuggestionComment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_suggestion")
	annotation= models.ForeignKey(Annotation, on_delete=models.CASCADE)
	suggestion = models.CharField(max_length=300)

	def serialize(self):
		return{

		"id": self.id,
		"user": self.user.username,
		"annotation": self.annotation.serialize(),
		"suggestion": self.suggestion

		}
		
