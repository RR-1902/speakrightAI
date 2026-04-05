from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    service: str


class TranscriptionResponse(BaseModel):
    filename: str
    language: str | None = None
    duration_seconds: float | None = None
    text: str
    model_used: str


class WordDifference(BaseModel):
    expected: str | None = None
    spoken: str | None = None


class PhonemeIssue(BaseModel):
    issue_type: str
    expected_phoneme: str | None = None
    actual_phoneme: str | None = None
    position: int | None = None
    message: str


class PhonemeWordAnalysis(BaseModel):
    word: str
    spoken_word: str | None = None
    expected_phonemes: list[str] = Field(default_factory=list)
    actual_phonemes: list[str] = Field(default_factory=list)
    issues: list[PhonemeIssue] = Field(default_factory=list)


class PronunciationComparisonResponse(BaseModel):
    filename: str
    session_id: str
    language: str | None = None
    duration_seconds: float | None = None
    model_used: str
    transcribed_text: str
    expected_text: str
    similarity_score: float
    pronunciation_score: int
    grade: str
    feedback: str
    attempts: int
    previous_scores: list[int] = Field(default_factory=list)
    word_differences: list[WordDifference] = Field(default_factory=list)
    phoneme_analysis: list[PhonemeWordAnalysis] = Field(default_factory=list)


class JsonAudioTranscriptionRequest(BaseModel):
    audio_base64: str
    expected_text: str
    filename: str = "audio.wav"
    session_id: str | None = None
