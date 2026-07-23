# SpeakRightAI Benchmark Report

Generated: 2026-07-23 20:58:19

## Resume Metrics Summary

| Metric | Result |
| --- | --- |
| Transcription latency avg | 0.89s |
| Transcription latency p95 | 1.07s |
| Full API response avg | 0.89s |
| Full API response p95 | 0.93s |
| Phoneme scoring accuracy | 85.0% |
| Soak test duration | 30.0 min |
| Crash/error count | 0 |

## Test Methodology

| Area | Method |
| --- | --- |
| Audio corpus | 30 generated WAV clips: 10 each at 5s, 15s, and 30s |
| Speech source | Synthetic spoken sentences normalized to 16 kHz mono WAV |
| Transcription model | Configured Whisper model running on CPU |
| Phoneme accuracy | 20 labeled expected/spoken text pairs evaluated through CMUdict scoring |
| Load test | Concurrent multipart uploads against the full FastAPI transcription endpoint |
| Uptime test | Health check polling every 10 seconds for 30 minutes |

## Transcription Latency By Clip Length

| Clip Length | Clips | Avg Transcription Time (s) | P95 (s) | Errors |
| --- | --- | --- | --- | --- |
| 5s | 10 | 0.91 | 1.56 | 0 |
| 15s | 10 | 0.87 | 1.02 | 0 |
| 30s | 10 | 0.89 | 1.07 | 0 |

## Full API Response Time By Clip Length

| Clip Length | Requests | Avg Response Time (s) | P95 (s) | Errors |
| --- | --- | --- | --- | --- |
| 5s | 10 | 0.99 | 2.38 | 0 |
| 15s | 10 | 0.84 | 0.88 | 0 |
| 30s | 10 | 0.85 | 0.92 | 0 |

## Phoneme Scoring Accuracy

| Cases | Correct | Accuracy |
| --- | --- | --- |
| 20 | 17 | 85.0% |

## Concurrent Request Handling

| Concurrent Users | Requests | Requests/sec | Avg Response (s) | P95 Response (s) | Error Rate |
| --- | --- | --- | --- | --- | --- |
| 10 | 10 | 1.21 | 4.63 | 8.23 | 0.0% |
| 25 | 25 | 1.20 | 10.87 | 20.00 | 0.0% |
| 50 | 50 | 1.20 | 21.49 | 40.03 | 0.0% |

## Uptime / Error Rate

| Duration | Health Checks | Failures | Error Rate | Avg Health Latency | P95 Health Latency |
| --- | --- | --- | --- | --- | --- |
| 30.0 min | 180 | 0 | 0.0% | 0.004s | 0.017s |

## Notes

- Transcription latency measures direct Whisper service execution for generated local speech clips.
- Full API response time measures upload, transcription, scoring, and response serialization.
- Load tests use 5-second clips to make 10, 25, and 50 concurrent request levels comparable.
- Phoneme accuracy is measured against a labeled text-pair test set.
