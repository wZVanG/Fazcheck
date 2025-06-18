# src/main.py

from transcripcion.whisper_transcriber import WhisperTranscriber
import math
import torch

def format_time(seconds: float):
	"""
	Convierte los segundos con decimales al formato SRT hh:mm:ss,ms
	"""
	hours = int(seconds // 3600)
	minutes = int((seconds % 3600) // 60)
	seconds = int(seconds % 60)
	milliseconds = int((seconds - int(seconds)) * 1000)
	return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def main():
	# Selecciona el transcriptor
	transcriber = WhisperTranscriber("small")

	path_audios = 'tmp/audios/'
	patch_transcripciones = 'tmp/transcripciones/'

	transcript_name = "Grabación.m4a"

	# Usa el transcriptor bases in transcript_name
	result = transcriber.transcribe(path_audios + transcript_name)

	file_txt_to_save = patch_transcripciones + transcript_name.split('.')[0] + '.txt'

	# # Get result.segments and create a srt file
	# with open(file_txt_to_save, 'w', encoding='utf-8') as f:
	# 	for i, segment in enumerate(result["segments"]):
	# 		f.write(str(i + 1) + '\n')
	# 		# Convierte los tiempos al formato SRT adecuado
	# 		start_time = format_time(segment["start"])
	# 		end_time = format_time(segment["end"])
	# 		f.write(f"{start_time} --> {end_time}\n")
	# 		f.write(segment["text"].strip() + '\n')
	# 		f.write('\n')
			
	 # Escribir cada fragmento de texto en una nueva línea
	with open(file_txt_to_save, 'w', encoding='utf-8') as f:
		for segment in result["segments"]:
			f.write(segment["text"].strip() + '\n')  # Agrega salto de línea después de cada fragmento

if __name__ == "__main__":
	main()
