from __future__ import annotations

from pathlib import Path
from threading import Lock

import whisper

from app.core.config import get_settings


class WhisperTranscriptionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        self._lock = Lock()

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = whisper.load_model(
                        self.settings.whisper_model,
                        device=self.settings.whisper_device,
                    )
        return self._model

    def transcribe(self, audio_path: Path) -> dict:
        model = self._get_model()
        result = model.transcribe(str(audio_path))
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language"),
            "duration_seconds": result.get("segments", [{}])[-1].get("end")
            if result.get("segments")
            else None,
            "model_used": self.settings.whisper_model,
        }


transcription_service = WhisperTranscriptionService()
