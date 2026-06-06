# SpeakRightAI

AI-powered pronunciation coach with:

- speech-to-text using Whisper
- phoneme-level pronunciation analysis
- pronunciation scoring and grading
- progress tracking across attempts

Repository:

- [RR-1902/speakrightAI](https://github.com/RR-1902/speakrightAI)

Live Link:

- [https://speakright-ai.vercel.app/](https://speakright-ai.vercel.app/)

---

## Deploy Fast

Use this production setup:

- Backend -> Render
- Frontend -> Vercel

Deploy order:

1. deploy backend on Render
2. copy backend URL
3. deploy frontend on Vercel
4. set `VITE_API_BASE_URL` to the Render backend URL
5. set backend `CORS_ORIGINS` to the Vercel frontend URL

---

## Architecture

```mermaid
flowchart LR
    A["User"] --> B["React Frontend<br/>Vercel"]
    B -->|POST audio + expected_text + session_id| C["FastAPI Backend<br/>Render"]
    C --> D["Whisper"]
    C --> E["Phoneme Analysis"]
    C --> F["Scoring + Feedback"]
    F --> B
```

Request flow:

1. user records or uploads audio
2. frontend sends audio to backend
3. backend transcribes audio with Whisper
4. backend compares text and phonemes
5. backend returns score, grade, feedback, and history
6. frontend displays results

---

## Stack

### Frontend

- React
- Vite
- Tailwind CSS
- Framer Motion

### Backend

- FastAPI
- Uvicorn
- OpenAI Whisper
- PyTorch
- NLTK CMUdict
- FFmpeg

---

## Local Run

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m nltk.downloader cmudict
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URLs:

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Important:

- `ffmpeg` must be installed and available in PATH
- use a clean virtual environment on Windows

### Frontend


```bash
npm install
npm run dev
```

Frontend URL:

- App: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## Environment Variables

### Backend

Supported:

- `APP_ENV`
- `WHISPER_MODEL`
- `WHISPER_DEVICE`
- `MAX_UPLOAD_SIZE_MB`
- `CORS_ORIGINS`

Example:

```bash
APP_ENV=production
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
MAX_UPLOAD_SIZE_MB=25
CORS_ORIGINS=https://speakright-ai.vercel.app
```

### Frontend

```bash
VITE_API_BASE_URL=https://speakrightai.onrender.com
```

---


Official docs:

- [Render Web Services](https://render.com/docs/web-services/)
- [Render Docker](https://render.com/docs/docker)

Official docs:

- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)


## Common Deployment Issues

### 1. Frontend loads but API calls fail

Check:

- `VITE_API_BASE_URL` is correct in Vercel
- backend is awake on Render
- `CORS_ORIGINS` matches the Vercel domain exactly

### 2. Render deploy succeeds but backend does not respond

Check:

- `/health` works
- Render logs show Uvicorn started
- `Dockerfile.backend` is being used

### 3. CORS error in browser

Fix:

- set backend `CORS_ORIGINS=https://speakright-ai.vercel.app`
- redeploy backend

### 4. Whisper is slow on first request

This is normal on cold start, especially on free hosting.

---

Run:

```bash
docker compose up --build
```

Local Docker URLs:

- frontend: [http://localhost:5173](http://localhost:5173)
- backend: [http://localhost:8000](http://localhost:8000)

---

## API

### Endpoints

- `GET /health`
- `POST /api/v1/speech/transcribe`

### Request fields

- `file`
- `expected_text`
- `session_id`

### Example cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/speech/transcribe" \
  -F "file=@sample.wav" \
  -F "expected_text=Hello and welcome to SpeakRightAI" \
  -F "session_id=demo-session-1"
```

---

## Current Limitations

- session tracking is in memory only
- Whisper cold starts can be slow
- CPU inference is slower than GPU inference
- large audio files take longer to process

---

## Next Improvements

1. move session history to a database
2. add authentication
3. store audio in cloud storage
4. add background jobs
5. add custom domains
