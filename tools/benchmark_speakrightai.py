from __future__ import annotations

import argparse
import gc
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ARTIFACT_DIR = ROOT / "benchmark_artifacts"
AUDIO_DIR = ARTIFACT_DIR / "audio"
REPORT_DIR = ROOT / "reports"
TRANSCRIBE_PATH = "/api/v1/speech/transcribe"


@dataclass(frozen=True)
class AudioCase:
    case_id: str
    expected_text: str
    duration_seconds: int
    path: Path


TEXT_CASES = [
    "The quick brown fox jumps over the lazy dog.",
    "Speak clearly and take a steady breath before each sentence.",
    "Practice makes pronunciation smoother over time.",
    "School children should slowly pronounce every sound.",
    "Think through the phrase and repeat it with confidence.",
    "The weather today is bright and pleasant.",
    "Artificial intelligence can support speech therapy practice.",
    "Please read this sentence at a natural pace.",
    "Strong pronunciation comes from careful listening.",
    "Three fresh flowers are growing near the garden.",
]


PHONEME_TEST_SET = [
    ("school", "school", True),
    ("school", "shool", False),
    ("three", "three", True),
    ("three", "tree", False),
    ("think", "think", True),
    ("think", "tink", False),
    ("yellow", "yellow", True),
    ("yellow", "jellow", False),
    ("chair", "chair", True),
    ("chair", "share", False),
    ("light", "light", True),
    ("light", "right", False),
    ("ship", "ship", True),
    ("ship", "sip", False),
    ("very clear speech", "very clear speech", True),
    ("practice every sound", "practice every sound", True),
    ("practice every sound", "practice airy sound", False),
    ("the quick brown fox", "the quick brown fox", True),
    ("the quick brown fox", "the quick brown box", False),
    ("fresh flowers", "fresh flours", False),
]


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = math.ceil((pct / 100) * len(sorted_values)) - 1
    return sorted_values[max(0, min(index, len(sorted_values) - 1))]


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def ensure_dirs() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def run_command(command: list[str], timeout: int = 120) -> None:
    subprocess.run(command, cwd=ROOT, check=True, timeout=timeout)


def synthesize_wav(text: str, output_path: Path) -> None:
    ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.Volume = 100
$synth.SetOutputToWaveFile('{str(output_path)}')
$synth.Speak('{text.replace("'", "''")}')
$synth.Dispose()
"""
    run_command(["powershell", "-NoProfile", "-Command", ps_script], timeout=60)


def normalize_duration(input_path: Path, output_path: Path, duration_seconds: int) -> None:
    run_command(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-af",
            "apad",
            "-t",
            str(duration_seconds),
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_path),
        ],
        timeout=120,
    )


def generate_audio_cases() -> list[AudioCase]:
    ensure_dirs()
    cases: list[AudioCase] = []
    durations = [5, 15, 30]

    for duration in durations:
        for index, text in enumerate(TEXT_CASES):
            case_id = f"{duration}s_{index + 1:02d}"
            final_path = AUDIO_DIR / f"{case_id}.wav"
            raw_path = AUDIO_DIR / f"{case_id}_raw.wav"

            if not final_path.exists():
                synthesize_wav(text, raw_path)
                normalize_duration(raw_path, final_path, duration)
                raw_path.unlink(missing_ok=True)

            cases.append(
                AudioCase(
                    case_id=case_id,
                    expected_text=text,
                    duration_seconds=duration,
                    path=final_path,
                )
            )

    return cases


def start_server_if_requested(start_server: bool, host: str, port: int) -> subprocess.Popen | None:
    if not start_server:
        return None

    env = os.environ.copy()
    env.setdefault("WHISPER_MODEL", "tiny")
    env.setdefault("WHISPER_DEVICE", "cpu")
    env.setdefault("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")

    server_log_path = ARTIFACT_DIR / "server.log"
    server_log = server_log_path.open("w", encoding="utf-8")

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=ROOT,
        env=env,
        stdout=server_log,
        stderr=subprocess.STDOUT,
        text=True,
    )

    wait_for_health(f"http://{host}:{port}", timeout_seconds=120)
    return process


def wait_for_health(base_url: str, timeout_seconds: int = 120) -> None:
    deadline = time.perf_counter() + timeout_seconds
    last_error = ""
    while time.perf_counter() < deadline:
        try:
            with request.urlopen(f"{base_url}/health", timeout=5) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # noqa: BLE001 - report startup errors.
            last_error = str(exc)
            time.sleep(2)
    raise RuntimeError(f"Backend did not become healthy: {last_error}")


def encode_multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----SpeakRightAIBenchmark{uuid.uuid4().hex}"
    parts: list[bytes] = []

    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(f"{value}\r\n".encode())

    file_bytes = file_path.read_bytes()
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode()
    )
    parts.append(b"Content-Type: audio/wav\r\n\r\n")
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())

    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def post_audio(base_url: str, case: AudioCase, timeout_seconds: int = 300) -> dict:
    body, content_type = encode_multipart(
        fields={
            "expected_text": case.expected_text,
            "session_id": f"benchmark-{uuid.uuid4().hex}",
        },
        file_field="file",
        file_path=case.path,
    )
    req = request.Request(
        f"{base_url}{TRANSCRIBE_PATH}",
        data=body,
        method="POST",
        headers={"Content-Type": content_type},
    )

    started = time.perf_counter()
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
            elapsed = time.perf_counter() - started
            return {
                "ok": True,
                "status": response.status,
                "elapsed_seconds": elapsed,
                "payload": payload,
                "error": "",
            }
    except error.HTTPError as exc:
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_seconds": elapsed,
            "payload": None,
            "error": exc.read().decode("utf-8", errors="replace"),
        }
    except Exception as exc:  # noqa: BLE001 - benchmark should capture all request failures.
        elapsed = time.perf_counter() - started
        return {
            "ok": False,
            "status": 0,
            "elapsed_seconds": elapsed,
            "payload": None,
            "error": str(exc),
        }


def measure_direct_transcription(cases: list[AudioCase]) -> list[dict]:
    from app.services.transcription import transcription_service

    rows: list[dict] = []
    for case in cases:
        started = time.perf_counter()
        try:
            result = transcription_service.transcribe(case.path)
            elapsed = time.perf_counter() - started
            rows.append(
                {
                    "case_id": case.case_id,
                    "duration_seconds": case.duration_seconds,
                    "elapsed_seconds": elapsed,
                    "transcribed_text": result.get("text", ""),
                    "ok": True,
                    "error": "",
                }
            )
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - started
            rows.append(
                {
                    "case_id": case.case_id,
                    "duration_seconds": case.duration_seconds,
                    "elapsed_seconds": elapsed,
                    "transcribed_text": "",
                    "ok": False,
                    "error": str(exc),
                }
            )
    transcription_service._model = None
    gc.collect()
    return rows


def measure_api_latency(base_url: str, cases: list[AudioCase]) -> list[dict]:
    rows: list[dict] = []
    for case in cases:
        result = post_audio(base_url, case)
        rows.append(
            {
                "case_id": case.case_id,
                "duration_seconds": case.duration_seconds,
                "elapsed_seconds": result["elapsed_seconds"],
                "status": result["status"],
                "ok": result["ok"],
                "error": result["error"],
            }
        )
    return rows


def measure_phoneme_accuracy() -> list[dict]:
    from app.services.comparison import comparison_service

    rows: list[dict] = []
    for index, (expected, spoken, should_pass) in enumerate(PHONEME_TEST_SET, start=1):
        result = comparison_service.compare(expected_text=expected, spoken_text=spoken)
        score = result["pronunciation_score"]
        predicted_pass = score >= 75
        rows.append(
            {
                "case_id": f"phoneme_{index:02d}",
                "expected_text": expected,
                "spoken_text": spoken,
                "expected_pass": should_pass,
                "predicted_pass": predicted_pass,
                "pronunciation_score": score,
                "correct": predicted_pass == should_pass,
            }
        )
    return rows


def measure_load(base_url: str, cases: list[AudioCase], concurrency_levels: list[int]) -> list[dict]:
    rows: list[dict] = []
    short_cases = [case for case in cases if case.duration_seconds == 5]
    if not short_cases:
        short_cases = cases[:1]

    for concurrency in concurrency_levels:
        selected_cases = [short_cases[index % len(short_cases)] for index in range(concurrency)]
        started = time.perf_counter()
        results = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(post_audio, base_url, case, 600) for case in selected_cases]
            for future in as_completed(futures):
                results.append(future.result())

        wall_seconds = time.perf_counter() - started
        success_count = sum(1 for item in results if item["ok"])
        error_count = len(results) - success_count
        latencies = [item["elapsed_seconds"] for item in results]
        rows.append(
            {
                "concurrency": concurrency,
                "total_requests": len(results),
                "success_count": success_count,
                "error_count": error_count,
                "error_rate_pct": (error_count / len(results)) * 100 if results else 0,
                "requests_per_second": len(results) / wall_seconds if wall_seconds else 0,
                "avg_response_seconds": mean(latencies),
                "p95_response_seconds": percentile(latencies, 95),
                "wall_seconds": wall_seconds,
            }
        )
    return rows


def measure_soak(base_url: str, minutes: float) -> dict:
    end_time = time.perf_counter() + (minutes * 60)
    total_checks = 0
    failures = 0
    latencies: list[float] = []

    while time.perf_counter() < end_time:
        started = time.perf_counter()
        try:
            with request.urlopen(f"{base_url}/health", timeout=10) as response:
                if response.status != 200:
                    failures += 1
        except Exception:  # noqa: BLE001
            failures += 1
        finally:
            total_checks += 1
            latencies.append(time.perf_counter() - started)
        time.sleep(10)

    return {
        "duration_minutes": minutes,
        "total_checks": total_checks,
        "failures": failures,
        "error_rate_pct": (failures / total_checks) * 100 if total_checks else 0,
        "avg_health_seconds": mean(latencies),
        "p95_health_seconds": percentile(latencies, 95),
    }


def table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def summarize_by_duration(rows: list[dict]) -> list[list[object]]:
    output = []
    for duration in sorted({row["duration_seconds"] for row in rows}):
        group = [row for row in rows if row["duration_seconds"] == duration]
        latencies = [row["elapsed_seconds"] for row in group if row["ok"]]
        output.append(
            [
                f"{duration}s",
                len(group),
                f"{mean(latencies):.2f}",
                f"{percentile(latencies, 95):.2f}",
                sum(1 for row in group if not row["ok"]),
            ]
        )
    return output


def write_reports(
    transcription_rows: list[dict],
    api_rows: list[dict],
    phoneme_rows: list[dict],
    load_rows: list[dict],
    soak_result: dict,
) -> Path:
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = REPORT_DIR / "benchmark_report.md"

    transcription_latencies = [row["elapsed_seconds"] for row in transcription_rows if row["ok"]]
    api_latencies = [row["elapsed_seconds"] for row in api_rows if row["ok"]]
    phoneme_accuracy = (
        sum(1 for row in phoneme_rows if row["correct"]) / len(phoneme_rows) * 100
        if phoneme_rows
        else 0
    )

    content = [
        "# SpeakRightAI Benchmark Report",
        "",
        f"Generated: {timestamp}",
        "",
        "## Resume Metrics Summary",
        "",
        table(
            ["Metric", "Result"],
            [
                ["Transcription latency avg", f"{mean(transcription_latencies):.2f}s"],
                ["Transcription latency p95", f"{percentile(transcription_latencies, 95):.2f}s"],
                ["Full API response avg", f"{mean(api_latencies):.2f}s"],
                ["Full API response p95", f"{percentile(api_latencies, 95):.2f}s"],
                ["Phoneme scoring accuracy", f"{phoneme_accuracy:.1f}%"],
                ["Soak test duration", f"{soak_result['duration_minutes']:.1f} min"],
                ["Crash/error count", soak_result["failures"]],
            ],
        ),
        "",
        "## Test Methodology",
        "",
        table(
            ["Area", "Method"],
            [
                ["Audio corpus", "30 generated WAV clips: 10 each at 5s, 15s, and 30s"],
                ["Speech source", "Synthetic spoken sentences normalized to 16 kHz mono WAV"],
                ["Transcription model", "Configured Whisper model running on CPU"],
                ["Phoneme accuracy", "20 labeled expected/spoken text pairs evaluated through CMUdict scoring"],
                ["Load test", "Concurrent multipart uploads against the full FastAPI transcription endpoint"],
                ["Uptime test", "Health check polling every 10 seconds for 30 minutes"],
            ],
        ),
        "",
        "## Transcription Latency By Clip Length",
        "",
        table(
            ["Clip Length", "Clips", "Avg Transcription Time (s)", "P95 (s)", "Errors"],
            summarize_by_duration(transcription_rows),
        ),
        "",
        "## Full API Response Time By Clip Length",
        "",
        table(
            ["Clip Length", "Requests", "Avg Response Time (s)", "P95 (s)", "Errors"],
            summarize_by_duration(api_rows),
        ),
        "",
        "## Phoneme Scoring Accuracy",
        "",
        table(
            ["Cases", "Correct", "Accuracy"],
            [[len(phoneme_rows), sum(1 for row in phoneme_rows if row["correct"]), f"{phoneme_accuracy:.1f}%"]],
        ),
        "",
        "## Concurrent Request Handling",
        "",
        table(
            [
                "Concurrent Users",
                "Requests",
                "Requests/sec",
                "Avg Response (s)",
                "P95 Response (s)",
                "Error Rate",
            ],
            [
                [
                    row["concurrency"],
                    row["total_requests"],
                    f"{row['requests_per_second']:.2f}",
                    f"{row['avg_response_seconds']:.2f}",
                    f"{row['p95_response_seconds']:.2f}",
                    f"{row['error_rate_pct']:.1f}%",
                ]
                for row in load_rows
            ],
        ),
        "",
        "## Uptime / Error Rate",
        "",
        table(
            ["Duration", "Health Checks", "Failures", "Error Rate", "Avg Health Latency", "P95 Health Latency"],
            [
                [
                    f"{soak_result['duration_minutes']:.1f} min",
                    soak_result["total_checks"],
                    soak_result["failures"],
                    f"{soak_result['error_rate_pct']:.1f}%",
                    f"{soak_result['avg_health_seconds']:.3f}s",
                    f"{soak_result['p95_health_seconds']:.3f}s",
                ]
            ],
        ),
        "",
        "## Notes",
        "",
        "- Transcription latency measures direct Whisper service execution for generated local speech clips.",
        "- Full API response time measures upload, transcription, scoring, and response serialization.",
        "- Load tests use 5-second clips to make 10, 25, and 50 concurrent request levels comparable.",
        "- Phoneme accuracy is measured against a labeled text-pair test set.",
    ]

    report_path.write_text("\n".join(content), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SpeakRightAI benchmark suite.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--start-server", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--soak-minutes", type=float, default=30.0)
    parser.add_argument("--concurrency", default="10,25,50")
    parser.add_argument("--max-cases", type=int, default=0)
    args = parser.parse_args()

    ensure_dirs()
    print("Generating benchmark audio clips...", flush=True)
    cases = generate_audio_cases()
    if args.max_cases > 0:
        cases = cases[: args.max_cases]
    print(f"Prepared {len(cases)} audio clips.", flush=True)

    server_process = None
    try:
        print("Measuring direct Whisper transcription latency...", flush=True)
        transcription_rows = measure_direct_transcription(cases)
        print("Measuring phoneme scoring accuracy...", flush=True)
        phoneme_rows = measure_phoneme_accuracy()

        print("Starting or checking FastAPI backend...", flush=True)
        server_process = start_server_if_requested(args.start_server, args.host, args.port)
        base_url = f"http://{args.host}:{args.port}" if args.start_server else args.base_url.rstrip("/")
        wait_for_health(base_url, timeout_seconds=120)

        print("Measuring full API response latency...", flush=True)
        api_rows = measure_api_latency(base_url, cases)
        concurrency_levels = [int(item.strip()) for item in args.concurrency.split(",") if item.strip()]
        print(f"Running load test for concurrency levels: {concurrency_levels}...", flush=True)
        load_rows = measure_load(base_url, cases, concurrency_levels)
        print(f"Running {args.soak_minutes:.1f}-minute uptime/error soak test...", flush=True)
        soak_result = measure_soak(base_url, args.soak_minutes)

        report_path = write_reports(
            transcription_rows=transcription_rows,
            api_rows=api_rows,
            phoneme_rows=phoneme_rows,
            load_rows=load_rows,
            soak_result=soak_result,
        )
        print(f"Benchmark report written to {report_path}")
        return 0
    finally:
        if server_process is not None:
            server_process.terminate()
            try:
                server_process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
