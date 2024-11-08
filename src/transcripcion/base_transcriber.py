# src/transcripcion/base_transcriber.py

from abc import ABC, abstractmethod

class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_file):
        """Transcribe an audio file and return the transcription."""
        pass

    @abstractmethod
    def get_model_info(self):
        """Return information about the transcription model."""
        pass
