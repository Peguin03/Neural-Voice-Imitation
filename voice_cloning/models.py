from django.db import models
from django.conf import settings
# from audiofield.fields import AudioField
import os.path
# Create your models here.

class Audio(models.Model):

	
	input_audio = models.FileField(upload_to='media/', 
		blank=True,
		help_text=("Allowed type - .wav, .ogg, .mp3, .m4a, .flac"))

	# cloned_audio = models.FileField(upload_to='media', 
	# 	blank=True,
	# 	help_text=("Allowed type - .wav, .ogg, .mp3, .m4a, .flac"))

