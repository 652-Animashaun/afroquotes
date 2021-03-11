from django.db import models
from django.contrib.auth.models import AbstractUser

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
	# verified= models.Boolean(default=False)

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
			"annotator": self.annotator.username
		}
		