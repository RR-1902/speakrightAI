# SpeakRightAI

SpeakRightAI is a full-stack AI pronunciation coach built to help users practice spoken English with AI-generated transcription, phoneme-aware feedback, scoring, and progress tracking.

Repository:

- [RR-1902/speakrightAI](https://github.com/RR-1902/speakrightAI)

Local project path:

- [C:\Users\vtr96\OneDrive\Documents\New project](/C:/Users/vtr96/OneDrive/Documents/New%20project)

---

## Overview

The application allows a user to:

1. enter an expected sentence
2. record audio or upload an audio file
3. transcribe speech using Whisper
4. compare expected text with spoken output
5. detect phoneme-level pronunciation issues
6. generate a pronunciation score and grade
7. track progress across attempts

---

## Tech Stack

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
|-- frontend/
|   |-- src/
|   |-- package.json
|   |-- vite.config.js
|   `-- Dockerfile
|-- Dockerfile.backend
|-- docker-compose.yml
|-- render.yaml
|-- requirements.txt
`-- README.md
```

---

## How It Works

### Backend flow

1. frontend sends `file`, `expected_text`, and `session_id`
2. backend receives the request at `POST /api/v1/speech/transcribe`
3. Whisper converts audio to text
4. text comparison calculates similarity
5. phoneme service converts words to phoneme sequences
6. scoring service computes:
   - similarity score
   - pronunciation score
   - grade
   - feedback
7. session tracker stores attempt history in memory

### Frontend flow

1. user enters expected text
2. user uploads audio or records with the microphone
3. frontend sends the request to the backend
4. frontend displays:
   - transcribed text
   - pronunciation score
   - grade
   - phoneme analysis
   - feedback
   - previous scores

---

## Run Locally

### Backend setup

From [C:\Users\vtr96\OneDrive\Documents\New project](/C:/Users/vtr96/OneDrive/Documents/New%20project):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m nltk.downloader cmudict
```

Important:

- `ffmpeg` must be installed and available in your system PATH
- Whisper depends on PyTorch
- on Windows, always use a clean virtual environment

### Run backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URLs:

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Frontend setup

From [C:\Users\vtr96\OneDrive\Documents\New project\frontend](/C:/Users/vtr96/OneDrive/Documents/New%20project/frontend):

```bash
npm install
npm run dev
```

Frontend URL:

- App: [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## Environment Variables

### Backend

Copy [.env.example](/C:/Users/vtr96/OneDrive/Documents/New%20project/.env.example) to `.env` if needed.

Supported backend variables:

- `APP_NAME`
- `APP_ENV`
- `API_V1_PREFIX`
- `WHISPER_MODEL`
- `WHISPER_DEVICE`
- `MAX_UPLOAD_SIZE_MB`
- `CORS_ORIGINS`

Example:

```bash
APP_ENV=development
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
MAX_UPLOAD_SIZE_MB=25
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

### Frontend

The frontend uses:

- `VITE_API_BASE_URL`

Local example:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

## Recommended Production Deployment

This project should be deployed like this:

- Backend -> Render
- Frontend -> Vercel

This is the recommended setup for this stack.

### Why not deploy the backend to Vercel or Netlify first?

Because the backend depends on:

- Whisper
- PyTorch
- FFmpeg
- NLTK corpus data
- uploaded audio processing

That makes it much heavier than a simple serverless function deployment.

Official references:

- [Vercel Functions Limits](https://vercel.com/docs/functions/limitations/)
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Netlify Functions Overview](https://docs.netlify.com/build/functions/overview)

---

## Deploy Backend To Render

This section is written as a direct step-by-step guide.

Render docs used:

- [Web Services](https://render.com/docs/web-services/)
- [Docker on Render](https://render.com/docs/docker)
- [Environment Variables and Secrets](https://render.com/docs/configure-environment-variables/)

### Step 1. Push your code to GitHub

Make sure your latest code is available in:

- [RR-1902/speakrightAI](https://github.com/RR-1902/speakrightAI)

### Step 2. Open Render

Go to:

- [https://render.com](https://render.com)

Sign in with your account.

### Step 3. Create a new Web Service

Inside Render:

1. click `New +`
2. click `Web Service`
3. connect GitHub if Render asks for permission
4. select:
   - `RR-1902/speakrightAI`

### Step 4. Fill the service form exactly like this

Use these values:

- Name: `speakrightai-backend`
- Region: choose the nearest region
- Branch: `main`
- Root Directory: leave empty
- Runtime: `Docker`

If Render asks for Dockerfile path, use:

```bash
Dockerfile.backend
```

### Step 5. Add environment variables

In the Render environment section, add:

```bash
APP_ENV=production
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
MAX_UPLOAD_SIZE_MB=25
CORS_ORIGINS=https://your-frontend-name.vercel.app
```

Important:

- replace `https://your-frontend-name.vercel.app` with your real Vercel URL after frontend deployment

### Step 6. Set health check path

Set this field to:

```bash
/health
```

### Step 7. Click Create Web Service

Render will now:

1. read [Dockerfile.backend](/C:/Users/vtr96/OneDrive/Documents/New%20project/Dockerfile.backend)
2. install FFmpeg
3. install Python dependencies
4. download NLTK `cmudict`
5. start FastAPI with Uvicorn

### Step 8. Wait for deployment to complete

When it succeeds, you will get a public URL like:

```bash
https://speakrightai-backend.onrender.com
```

### Step 9. Test the backend

Open these URLs:

- `https://your-backend.onrender.com/health`
- `https://your-backend.onrender.com/docs`

Expected result:

- `/health` should respond successfully
- `/docs` should open Swagger UI

### Step 10. Save the backend URL

You will need it for Vercel.

Example:

```bash
https://speakrightai-backend.onrender.com
```

---

## Deploy Frontend To Vercel

Vercel docs used:

- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)

### Step 1. Open Vercel

Go to:

- [https://vercel.com](https://vercel.com)

### Step 2. Create a new project

Inside Vercel:

1. click `Add New`
2. click `Project`
3. import:
   - `RR-1902/speakrightAI`

### Step 3. Set the root directory

This is very important.

Set:

```bash
frontend
```

### Step 4. Confirm the build settings

Use:

- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

### Step 5. Add the frontend environment variable

Set:

```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

Example:

```bash
VITE_API_BASE_URL=https://speakrightai-backend.onrender.com
```

### Step 6. Deploy

Click `Deploy`.

After deployment, your frontend URL will look like:

```bash
https://speakrightai.vercel.app
```

### Step 7. Update Render CORS if needed

Now take your final Vercel production URL and make sure Render allows it.

Your Render backend environment variable should be:

```bash
CORS_ORIGINS=https://your-frontend-name.vercel.app
```

If needed:

1. open the backend service in Render
2. go to `Environment`
3. update `CORS_ORIGINS`
4. save changes
5. redeploy

---

## Final Production Test

After both are deployed:

1. open the Vercel frontend
2. enter an expected sentence
3. upload audio or record audio
4. click analyze
5. confirm the results appear correctly

You should see:

- transcribed text
- pronunciation score
- grade
- phoneme analysis
- feedback
- progress history

---

## Production Checklist

### Backend

- repo connected in Render
- runtime set to Docker
- `Dockerfile.backend` used
- environment variables added
- `/health` works
- `/docs` works

### Frontend

- repo connected in Vercel
- root directory set to `frontend`
- `VITE_API_BASE_URL` set correctly
- deploy completed successfully

### Browser test

- frontend loads
- backend health works
- frontend can submit audio
- results appear without CORS errors

---

## Docker

Docker support is included for local full-stack runs.

Files:

- [Dockerfile.backend](/C:/Users/vtr96/OneDrive/Documents/New%20project/Dockerfile.backend)
- [frontend/Dockerfile](/C:/Users/vtr96/OneDrive/Documents/New%20project/frontend/Dockerfile)
- [docker-compose.yml](/C:/Users/vtr96/OneDrive/Documents/New%20project/docker-compose.yml)

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

- session progress is stored in memory only
- Whisper cold starts can be slow
- CPU inference is slower than GPU inference
- large uploads may take longer to process

---

## Recommended Next Improvements

1. move progress tracking to a database
2. add authentication
3. store audio in cloud storage if needed
4. add background job processing
5. add custom production domains
