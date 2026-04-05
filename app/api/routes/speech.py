from __future__ import annotations

import base64
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.core.config import get_settings
from app.models.speech import JsonAudioTranscriptionRequest, PronunciationComparisonResponse
from app.services.comparison import comparison_service
from app.services.scoring import attempt_tracker
from app.services.transcription import transcription_service

router = APIRouter(prefix="/speech", tags=["speech"])

ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".webm",
    ".ogg",
}


def _validate_audio_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: '{suffix or 'unknown'}'.",
        )
    return suffix


def _validate_expected_text(expected_text: str | None) -> str:
    if expected_text is None or not expected_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expected_text is required for pronunciation comparison.",
        )
    return expected_text.strip()


async def _extract_request_payload(
    request: Request,
    file: UploadFile | None,
    expected_text: str | None,
    payload: str | None,
    session_id: str | None,
) -> tuple[str, bytes, str, str]:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body = JsonAudioTranscriptionRequest.model_validate(await request.json())
            audio_bytes = base64.b64decode(body.audio_base64)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON audio payload: {exc}",
            ) from exc
        return (
            body.filename,
            audio_bytes,
            _validate_expected_text(body.expected_text),
            attempt_tracker.get_or_create_session_id(body.session_id),
        )

    resolved_expected_text = expected_text
    resolved_session_id = session_id
    if payload:
        try:
            payload_data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON payload field: {exc}",
            ) from exc
        resolved_expected_text = payload_data.get("expected_text", resolved_expected_text)
        resolved_session_id = payload_data.get("session_id", resolved_session_id)

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="audio file is required for multipart requests.",
        )

    return (
        file.filename or "audio.wav",
        await file.read(),
        _validate_expected_text(resolved_expected_text),
        attempt_tracker.get_or_create_session_id(resolved_session_id),
    )


@router.post("/transcribe", response_model=PronunciationComparisonResponse)
async def transcribe_audio(
    request: Request,
    file: UploadFile | None = File(default=None),
    expected_text: str | None = Form(default=None),
    payload: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
) -> PronunciationComparisonResponse:
    settings = get_settings()
    filename, contents, resolved_expected_text, resolved_session_id = await _extract_request_payload(
        request=request,
        file=file,
        expected_text=expected_text,
        payload=payload,
        session_id=session_id,
    )
    suffix = _validate_audio_extension(filename)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_size_mb} MB limit.",
        )

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_path = Path(temp_file.name)

        transcription_result = transcription_service.transcribe(temp_path)
        comparison_result = comparison_service.compare(
            expected_text=resolved_expected_text,
            spoken_text=transcription_result["text"],
        )
        tracking_result = attempt_tracker.record_attempt(
            session_id=resolved_session_id,
            score=comparison_result["pronunciation_score"],
        )
        return PronunciationComparisonResponse(
            filename=filename,
            session_id=resolved_session_id,
            language=transcription_result.get("language"),
            duration_seconds=transcription_result.get("duration_seconds"),
            model_used=transcription_result["model_used"],
            attempts=tracking_result["attempts"],
            previous_scores=tracking_result["previous_scores"],
            **comparison_result,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {exc}",
        ) from exc
    finally:
        if "temp_path" in locals() and temp_path.exists():
            temp_path.unlink(missing_ok=True)
