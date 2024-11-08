import os
import whisper
import torch
import threading
import time  # Para medir el tiempo de transcripción
from .base_transcriber import BaseTranscriber

class WhisperTranscriber(BaseTranscriber):
	def __init__(self, model_name="base"):
		print("Cargando modelo: ", model_name)    
		self.model = whisper.load_model(model_name)
		self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
		print(f"Dispositivo a utilizar: {self.device}")

	def _loader(self, stop_event, start_time):
		"""Función que muestra un loader y el tiempo transcurrido en la consola mientras se transcribe el audio."""
		loader_symbols = ['|', '/', '-', '\\']
		idx = 0
		while not stop_event.is_set():
			elapsed_time = time.time() - start_time
			minutes, seconds = divmod(int(elapsed_time), 60)
			time_str = f"{minutes:02}:{seconds:02}"
			print(f"\rTranscribiendo... {loader_symbols[idx % len(loader_symbols)]} - Tiempo transcurrido: {time_str}", end="", flush=True)
			idx += 1
			time.sleep(0.1)  # Controla la velocidad de animación

	def transcribe(self, audio_file):
		if not os.path.isfile(audio_file):
			raise FileNotFoundError(f"El archivo {audio_file} no existe.")
		
		stop_event = threading.Event()
		start_time = time.time()  # Marca el inicio de la transcripción
		
		loader_thread = threading.Thread(target=self._loader, args=(stop_event, start_time))
		
		try:
			loader_thread.start()  # Iniciar el loader
			result = self.model.transcribe(audio_file)
		finally:
			stop_event.set()  # Detener el loader
			loader_thread.join()  # Esperar a que termine el hilo
			print("\rTranscripción completada.                                        ")  # Limpiar el loader de la consola

		end_time = time.time()  # Marca el final de la transcripción
		transcription_time = end_time - start_time  # Calcula el tiempo transcurrido
		
		print(f"Tiempo total de transcripción: {transcription_time:.2f} segundos")

		return result

	def get_model_info(self):
		return {"model_name": self.model.name}
