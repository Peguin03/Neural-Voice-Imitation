from django.shortcuts import render

# Create your views here.
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
# from django.core.urlresolvers import reverse
#from .models import Audio
#from .forms import AudioForm


from .encoder.params_model import model_embedding_size as speaker_embedding_size
from .utils.argutils import print_args
from .utils.modelutils import check_model_paths
from .synthesizer.inference import Synthesizer
from .encoder import inference as encoder
from .vocoder import inference as vocoder

from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import argparse
import torch
import sys
import os
from audioread.exceptions import NoBackendError

import random
import string
import time
import wave


from Crypto.Cipher import AES
from scipy.io import wavfile
from tqdm import tqdm

import io
import struct







def gettingready_aes():

	# global AES_KEY
	AES_KEY=""
	AES_KEY = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits+string.ascii_uppercase + string.ascii_lowercase + string.digits+string.ascii_uppercase + string.digits + string.ascii_lowercase ) for x in range(32))
	
	# global AES_IV
	AES_IV=""
	AES_IV = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits+string.ascii_uppercase + string.ascii_lowercase + string.digits+string.ascii_uppercase + string.digits + string.ascii_lowercase ) for x in range(16))
	return AES_KEY, AES_IV




def encrypt_aes(filename_aes, AES_KEY, AES_IV):
    # Taking input
	
	with open(filename_aes, 'rb') as fd:
		contents = fd.read()
    # Encrpytion of audio file
	encryptor = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CFB, AES_IV.encode("utf-8"))
	encrypted_audio = encryptor.encrypt(contents)
	fileLoc=filename_aes[:-4]+'_AES_Encrypted.wav'
	with open(fileLoc, 'wb') as fd:
		fd.write(encrypted_audio)
	print(f"An encrypted audio file is generated and stored at {fileLoc}. ")
	return(fileLoc)



def decrypt_aes(encrypted_aes, AES_KEY, AES_IV):

	with open(encrypted_aes, 'rb') as fd:
		contents1 = fd.read()

    # Decryption of data
	decryptor = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CFB, AES_IV.encode("utf-8"))
	decrypted_audio = decryptor.decrypt(contents1)
	#fileLoc=encrypted_aes[:-4]+'AES_Decrypted.wav'
	decrypted_audio_object = io.BytesIO(decrypted_audio)
	print(f"Decrypted file objected generated. ")
	return(decrypted_audio_object)


def index(request):
	context = {}#'a': 1
	return(render(request, 'index.html', context))


def cloneVoice(request):
	# print(request)
	# print(request.POST.dict())

	file = request.FILES['filePath']
	text = request.POST.get("myTextBox",'')
	fs = FileSystemStorage()
	filepathName = fs.save(file.name,file)
	filepathName = fs.url(filepathName)
	og_fpath = str(settings.BASE_DIR) + str(filepathName)
	AES_KEY, AES_IV = gettingready_aes()
	fpath = encrypt_aes(og_fpath, AES_KEY, AES_IV)#returns absolute location of encrypted file 
	os.remove(og_fpath)
	

	fpath = Path(fpath)#instance.input_audio.path#


	#No mp3 files!!!!
	while(fpath.suffix.lower() == ".mp3" ):
		print("Can't Use mp3 files please try again:")
		
	
	in_fpath=decrypt_aes(fpath, AES_KEY, AES_IV)

	#preprocessed_wav = encoder.preprocess_wav(in_fpath)
	encoder.load_model(str(settings.BASE_DIR) + '/voice_cloning/encoder/saved_models/pretrained.pt')
	synthesizer = Synthesizer(str(settings.BASE_DIR) + '/voice_cloning/synthesizer/saved_models/pretrained.pt')
	vocoder.load_model(str(settings.BASE_DIR) + '/voice_cloning/vocoder/saved_models/pretrained.pt')
	original_wav, sampling_rate = librosa.load(in_fpath,sr=22050)#sr value hard coded
	preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)

	embed = encoder.embed_utterance(preprocessed_wav)

	synthesizer = Synthesizer(str(settings.BASE_DIR) + '/voice_cloning/synthesizer/saved_models/pretrained.pt')

	texts = [text]
	embeds = [embed]

	specs = synthesizer.synthesize_spectrograms(texts, embeds)
	spec = specs[0]

	vocoder.load_model(str(settings.BASE_DIR) + '/voice_cloning/vocoder/saved_models/pretrained.pt')

	generated_wav = vocoder.infer_waveform(spec)

	generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")

	generated_wav = encoder.preprocess_wav(generated_wav)

	outputFileName = str(settings.BASE_DIR)+str(settings.MEDIA_URL)+ 'cloned_voice.wav'
	sf.write(outputFileName, generated_wav.astype(np.float32),synthesizer.sample_rate)
	
	# outputFileName = fs.save('output.wav', outputFileName)
	# outputFileName = fs.url(outputFileName)
	#context = {'filepathName':filepathName}
	context = {'outputFileName' : settings.MEDIA_URL+'cloned_voice.wav'}
	return render(request, 'index.html', context)
