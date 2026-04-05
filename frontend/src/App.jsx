import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  AudioLines,
  LoaderCircle,
  Mic,
  Radio,
  Sparkles,
  Trash2,
  UploadCloud,
  WandSparkles,
} from "lucide-react";
import { GlassPanel } from "./components/GlassPanel";
import { ResultCard } from "./components/ResultCard";
import { submitPronunciation } from "./lib/api";
import { useRecorder } from "./lib/useRecorder";

const initialFormState = {
  expectedText: "",
};

const SESSION_STORAGE_KEY = "speakrightai-session-id";

function createSessionId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function App() {
  const fileInputRef = useRef(null);
  const [formState, setFormState] = useState(initialFormState);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [phonemeOpen, setPhonemeOpen] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const {
    isRecording,
    recordedFile,
    recordingTime,
    recorderError,
    startRecording,
    stopRecording,
    clearRecording,
  } = useRecorder();

  const activeAudioFile = recordedFile ?? selectedFile;

  useEffect(() => {
    const storedSessionId = window.localStorage.getItem(SESSION_STORAGE_KEY);
    if (storedSessionId) {
      setSessionId(storedSessionId);
      return;
    }

    const nextSessionId = createSessionId();
    window.localStorage.setItem(SESSION_STORAGE_KEY, nextSessionId);
    setSessionId(nextSessionId);
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!formState.expectedText.trim()) {
      setError("Enter the sentence you want the user to pronounce.");
      return;
    }

    if (!activeAudioFile) {
      setError("Upload an audio file or record with your microphone before starting the analysis.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await submitPronunciation({
        expectedText: formState.expectedText.trim(),
        sessionId,
        file: activeAudioFile,
      });

      setResult(data);
      setPhonemeOpen(Boolean(data.phoneme_analysis?.length));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleFileChange(event) {
    const nextFile = event.target.files?.[0] ?? null;
    setSelectedFile(nextFile);
    if (nextFile) {
      clearRecording();
    }
  }

  async function handleRecordingToggle() {
    setError("");

    if (isRecording) {
      stopRecording();
      return;
    }

    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    await startRecording();
  }

  function handleClearAudio() {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    clearRecording();
  }

  function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  function handleResetProgress() {
    const nextSessionId = createSessionId();
    window.localStorage.setItem(SESSION_STORAGE_KEY, nextSessionId);
    setSessionId(nextSessionId);
    setResult(null);
    setSelectedFile(null);
    setPhonemeOpen(true);
    setError("");
    clearRecording();

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-aurora text-ink">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[8%] top-20 h-56 w-56 rounded-full bg-fuchsia-300/20 blur-3xl" />
        <div className="absolute right-[10%] top-32 h-72 w-72 rounded-full bg-indigo-300/20 blur-3xl" />
        <div className="absolute bottom-[-6rem] left-1/2 h-80 w-80 -translate-x-1/2 rounded-full bg-violet-300/15 blur-3xl" />
      </div>

      <main className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-10 sm:px-6 lg:px-8">
        <section className="mx-auto w-full max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8 text-center"
          >
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/75 shadow-glow backdrop-blur-xl">
              <Sparkles className="h-4 w-4 text-violet-100" />
              Premium AI Pronunciation Intelligence
            </div>
            <h1 className="font-display text-5xl font-semibold tracking-tight text-white md:text-7xl">
              SpeakRightAI
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-white/72 md:text-xl">
              AI-Powered Pronunciation Coach
            </p>
          </motion.div>

          <GlassPanel className="relative overflow-hidden p-6 md:p-8">
            <div className="absolute right-0 top-0 h-48 w-48 rounded-full bg-white/10 blur-3xl" />
            <div className="relative grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
              <div>
                <div className="mb-6 inline-flex items-center gap-3 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-xs uppercase tracking-[0.3em] text-white/70">
                  <WandSparkles className="h-4 w-4" />
                  Live Analysis Console
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                  <label className="block">
                    <span className="mb-3 block text-sm uppercase tracking-[0.3em] text-white/55">
                      Expected sentence
                    </span>
                    <textarea
                      rows={4}
                      value={formState.expectedText}
                      onChange={(event) =>
                        setFormState((current) => ({
                          ...current,
                          expectedText: event.target.value,
                        }))
                      }
                      placeholder="Enter expected sentence"
                      className="w-full rounded-[24px] border border-white/15 bg-white/10 px-5 py-4 font-body text-base text-white placeholder:text-white/35 outline-none transition focus:border-violet-200/50 focus:bg-white/12"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-3 block text-sm uppercase tracking-[0.3em] text-white/55">
                      Session tracking
                    </span>
                    <div className="flex flex-col gap-3 rounded-[20px] border border-white/15 bg-white/8 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-white/80">Progress tracking is active automatically.</p>
                        <p className="mt-1 text-xs text-white/45">Session: {sessionId || "Initializing..."}</p>
                      </div>
                      <button
                        type="button"
                        onClick={handleResetProgress}
                        disabled={loading || isRecording}
                        className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/8 px-4 py-2 text-sm text-white/80 transition hover:bg-white/12 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Reset Progress
                      </button>
                    </div>
                  </label>

                  <div className="rounded-[28px] border border-dashed border-white/20 bg-white/8 p-5">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm uppercase tracking-[0.3em] text-white/55">Audio Input</p>
                        <p className="mt-2 text-sm text-white/65">
                          Upload a file or record a fresh sample with your microphone.
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-3">
                        <button
                          type="button"
                          onClick={() => fileInputRef.current?.click()}
                          disabled={isRecording}
                          className="inline-flex items-center justify-center gap-3 rounded-full border border-white/15 bg-white/10 px-5 py-3 text-sm text-white transition hover:scale-[1.02] hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <UploadCloud className="h-4 w-4" />
                          Choose File
                        </button>

                        <motion.button
                          type="button"
                          onClick={handleRecordingToggle}
                          whileHover={{ scale: isRecording ? 1 : 1.03 }}
                          whileTap={{ scale: 0.98 }}
                          disabled={loading}
                          className={`inline-flex items-center justify-center gap-3 rounded-full px-5 py-3 text-sm text-white transition disabled:cursor-not-allowed disabled:opacity-60 ${
                            isRecording
                              ? "border border-red-200/30 bg-gradient-to-r from-rose-500 to-red-500 shadow-[0_0_0_1px_rgba(255,255,255,0.08),0_0_36px_rgba(255,69,100,0.45)]"
                              : "border border-fuchsia-200/20 bg-gradient-to-r from-fuchsia-500/90 via-violet-500/90 to-indigo-400/90 shadow-button"
                          }`}
                        >
                          {isRecording ? (
                            <>
                              <Radio className="h-4 w-4 animate-pulse" />
                              Stop Recording
                            </>
                          ) : (
                            <>
                              <Mic className="h-4 w-4" />
                              Start Recording
                            </>
                          )}
                        </motion.button>
                      </div>
                    </div>

                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".wav,.mp3,.m4a,.mp4,.mpeg,.mpga,.webm,.ogg,audio/*"
                      className="hidden"
                      onChange={handleFileChange}
                    />

                    <div className="mt-4 space-y-3">
                      <AnimatePresence>
                        {isRecording ? (
                          <motion.div
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            className="flex items-center justify-between rounded-2xl border border-red-200/20 bg-red-400/10 px-4 py-3 text-sm text-red-100"
                          >
                            <div className="flex items-center gap-3">
                              <span className="h-3 w-3 rounded-full bg-red-400 shadow-[0_0_18px_rgba(248,113,113,0.85)]" />
                              <span>Recording...</span>
                            </div>
                            <span className="font-display text-base">{formatDuration(recordingTime)}</span>
                          </motion.div>
                        ) : null}
                      </AnimatePresence>

                      <div className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-sm text-white/78">
                        {activeAudioFile ? (
                          <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                              <span className="font-medium text-white">{activeAudioFile.name}</span>
                              <span className="ml-2 text-white/45">
                                {(activeAudioFile.size / (1024 * 1024)).toFixed(2)} MB
                              </span>
                              <span className="ml-2 rounded-full bg-white/8 px-2 py-1 text-xs text-white/60">
                                {recordedFile ? "Recorded clip" : "Uploaded file"}
                              </span>
                            </div>
                            <button
                              type="button"
                              onClick={handleClearAudio}
                              disabled={isRecording || loading}
                              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-2 text-xs text-white/70 transition hover:bg-white/12 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                              Clear
                            </button>
                          </div>
                        ) : (
                          "No audio selected yet."
                        )}
                      </div>
                    </div>

                    <div className="mt-4 rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-sm text-white/78">
                      {recordedFile ? (
                        "Recorded audio is ready to analyze."
                      ) : selectedFile ? (
                        <>
                          Uploaded audio is ready to analyze.
                        </>
                      ) : (
                        "Choose a file or start recording to create a voice sample."
                      )}
                    </div>
                  </div>

                  <AnimatePresence>
                    {recorderError ? (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="rounded-[20px] border border-amber-200/15 bg-amber-300/10 px-5 py-4 text-sm text-amber-100"
                      >
                        {recorderError}
                      </motion.div>
                    ) : null}
                  </AnimatePresence>

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    disabled={loading || isRecording}
                    type="submit"
                    className="inline-flex w-full items-center justify-center gap-3 rounded-full bg-gradient-to-r from-fuchsia-500 via-violet-500 to-indigo-400 px-6 py-4 font-display text-lg font-medium text-white shadow-button transition disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {loading ? (
                      <>
                        <LoaderCircle className="h-5 w-5 animate-spin" />
                        Analyzing pronunciation...
                      </>
                    ) : (
                      <>
                        <AudioLines className="h-5 w-5" />
                        Analyze Pronunciation
                      </>
                    )}
                  </motion.button>
                </form>

                <AnimatePresence>
                  {error ? (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="mt-5 rounded-[20px] border border-rose-200/15 bg-rose-300/10 px-5 py-4 text-sm text-rose-100"
                    >
                      {error}
                    </motion.div>
                  ) : null}
                </AnimatePresence>
              </div>

              <div className="flex flex-col justify-between gap-5">
                <div className="rounded-[30px] border border-white/15 bg-gradient-to-br from-white/18 to-white/6 p-6 shadow-glow">
                  <p className="text-xs uppercase tracking-[0.35em] text-white/45">What you get</p>
                  <div className="mt-6 space-y-4">
                    {[
                      "Whisper-powered transcription from your uploaded speech",
                      "Pronunciation scoring with phoneme-aware AI analysis",
                      "Session-based progress tracking for repeat attempts",
                    ].map((item) => (
                      <div
                        key={item}
                        className="flex items-start gap-3 rounded-2xl border border-white/10 bg-black/10 px-4 py-4 text-white/82"
                      >
                        <div className="mt-1 h-2.5 w-2.5 rounded-full bg-gradient-to-r from-fuchsia-300 to-violet-200 shadow-glow" />
                        <p className="leading-7">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-[24px] border border-white/10 bg-white/8 p-5">
                    <p className="text-xs uppercase tracking-[0.3em] text-white/45">Response speed</p>
                    <p className="mt-3 font-display text-3xl text-white">FastAPI + Vite</p>
                    <p className="mt-2 text-sm text-white/60">Optimized for quick iteration and clean API integration.</p>
                  </div>
                  <div className="rounded-[24px] border border-white/10 bg-white/8 p-5">
                    <p className="text-xs uppercase tracking-[0.3em] text-white/45">Coaching depth</p>
                    <p className="mt-3 font-display text-3xl text-white">Phoneme-first</p>
                    <p className="mt-2 text-sm text-white/60">Surfacing real sound-level pronunciation issues, not just text mismatches.</p>
                  </div>
                </div>
              </div>
            </div>
          </GlassPanel>

          <div className="mt-8">
            <AnimatePresence mode="wait">
              {result ? (
                <ResultCard
                  key={result.session_id + result.attempts}
                  result={result}
                  phonemeOpen={phonemeOpen}
                  onTogglePhoneme={() => setPhonemeOpen((current) => !current)}
                />
              ) : (
                <motion.div
                  key="empty-state"
                  initial={{ opacity: 0, y: 18 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -18 }}
                >
                  <GlassPanel className="p-8 text-center">
                    <div className="mx-auto flex h-20 w-20 animate-pulseSoft items-center justify-center rounded-full border border-white/15 bg-white/10">
                      <Sparkles className="h-8 w-8 text-violet-100" />
                    </div>
                    <h2 className="mt-6 font-display text-3xl text-white">Your AI coaching results will appear here</h2>
                    <p className="mx-auto mt-3 max-w-2xl text-lg leading-8 text-white/62">
                      Upload a voice sample, define the expected sentence, and SpeakRightAI will return pronunciation score, grade, phoneme breakdown, and progress history.
                    </p>
                  </GlassPanel>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>
      </main>
    </div>
  );
}
