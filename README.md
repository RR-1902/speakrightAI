# SpeakRightAI

SpeakRightAI is a modular speech therapy assistant backend built with FastAPI.

## Phase 1 Goal

Phase 1 focuses on one clean responsibility:

- accept an audio upload
- run Whisper automatic speech recognition (ASR)
- return the transcribed text as JSON

## Phase 2 Goal

Phase 2 adds a pronunciation comparison engine:

- accept `expected_text` alongside audio
- compare spoken output with expected text
- compute a similarity score
- return actionable feedback and word-level differences

## Phase 3 Goal

Phase 3 adds phoneme-level pronunciation analysis:

- convert expected and spoken words into phoneme sequences
- compare phoneme sequences word by word
- detect missing, extra, and substituted sounds
- generate more specific pronunciation feedback

## Phase 4 Goal

Phase 4 makes the API feel product-ready:

- convert similarity into a `0-100` pronunciation score
- classify performance into grades
- return more actionable coaching feedback
- track attempts per session in memory

## Project Structure

```text
SpeakRightAI/
|-- app/
|   |-- api/routes/
|   |   |-- health.py
|   |   `-- speech.py
|   |-- core/config.py
|   |-- models/speech.py
|   |-- services/comparison.py
|   |-- services/phoneme.py
|   |-- services/scoring.py
|   |-- services/transcription.py
|   `-- main.py
|-- .env.example
`-- requirements.txt
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` if you want to override defaults.
4. The first phoneme-analysis request will download the NLTK `cmudict` corpus automatically if needed.

## Run

```bash
uvicorn app.main:app --reload
```

Open the API docs at `http://127.0.0.1:8000/docs`.

## Frontend

The React frontend lives in `frontend/` and is built with Vite, Tailwind CSS, and Framer Motion.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://127.0.0.1:5173` and proxies `/api/*` requests to the FastAPI backend.

If you want to call a different backend host, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.

## Endpoints

- `GET /health`
- `POST /api/v1/speech/transcribe`

### Example response

```json
{
  "filename": "sample.wav",
  "session_id": "demo-session-1",
  "language": "en",
  "duration_seconds": 3.24,
  "model_used": "tiny",
  "transcribed_text": "hello and welcome to speak right ai",
  "expected_text": "Hello and welcome to SpeakRightAI",
  "similarity_score": 0.9474,
  "pronunciation_score": 95,
  "grade": "Excellent",
  "feedback": "Excellent pronunciation. Your speech closely matches the expected text. Keep practicing with short repetitions and listen closely to the target pronunciation.",
  "attempts": 3,
  "previous_scores": [88, 92, 95],
  "word_differences": [],
  "phoneme_analysis": []
}
```

### Example with phoneme issues

```json
{
  "session_id": "demo-session-2",
  "transcribed_text": "shool",
  "expected_text": "school",
  "similarity_score": 0.6429,
  "pronunciation_score": 64,
  "grade": "Needs Improvement",
  "feedback": "Good attempt. Minor pronunciation differences detected. You missed the 'k' sound in 'school'. You missed the 'k' sound and you replaced 's' with 'sh'. Try slowing down and emphasizing the missing consonant sound.",
  "attempts": 2,
  "previous_scores": [51, 64],
  "phoneme_analysis": [
    {
      "word": "school",
      "spoken_word": "shool",
      "expected_phonemes": ["S", "K", "UW", "L"],
      "actual_phonemes": ["SH", "UW", "L"],
      "issues": [
        {
          "issue_type": "substitution",
          "expected_phoneme": "S",
          "actual_phoneme": "SH",
          "position": 0,
          "message": "In 'school', the 's' sound was pronounced more like 'sh'."
        },
        {
          "issue_type": "missing",
          "expected_phoneme": "K",
          "actual_phoneme": null,
          "position": 1,
          "message": "You missed the 'k' sound in 'school'."
        }
      ]
    }
  ]
}
```

### Multipart form example

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/speech/transcribe" \
  -F "file=@sample.wav" \
  -F "expected_text=Hello and welcome to SpeakRightAI" \
  -F "session_id=demo-session-1"
```

### JSON with base64 audio example

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/speech/transcribe" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"sample.wav\",\"expected_text\":\"Hello and welcome to SpeakRightAI\",\"audio_base64\":\"<BASE64_AUDIO>\",\"session_id\":\"demo-session-1\"}"
```

## Important Note About Whisper

`openai-whisper` depends on `ffmpeg` being installed and available on your system path.

## How Phoneme Analysis Works

1. `expected_text` and `transcribed_text` are tokenized into words.
2. Each word is converted to ARPABET phonemes using NLTK CMUdict.
3. If a word is not found in CMUdict, a small rule-based fallback approximates the phonemes.
4. The system compares phoneme sequences with `difflib.SequenceMatcher`.
5. It reports missing, extra, and substituted sounds in a structured `phoneme_analysis` field.

## Scoring And Tracking

1. `text_similarity` is computed from normalized text matching.
2. `phoneme_similarity` is computed from aligned phoneme sequences.
3. The final score uses the Phase 4 weighting:
   `overall = (phoneme_similarity * 0.7) + (text_similarity * 0.3)`
4. The score is scaled to `0-100` and mapped to a grade.
5. Attempts are tracked in memory by `session_id`, returning `attempts` and `previous_scores`.

Because tracking is in memory, scores reset when the server restarts. This keeps the implementation simple now and easy to replace with a database later.

## Next Phases

- Phase 4: add TTS output, progress tracking, and real-time feedback
