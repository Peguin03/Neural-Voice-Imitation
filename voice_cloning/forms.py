from django import forms
from .models import Audio

class AudioForm(forms.ModelForm):
	class Meta:
		model = Audio
		fields = {'input_audio'}
	#audiofile = forms.FileField(label='Select a file')