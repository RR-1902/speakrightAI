import { useEffect, useRef, useState } from "react";

function getSupportedMimeType() {
  if (typeof MediaRecorder === "undefined") {
    return "";
  }

  const preferredTypes = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];

  return preferredTypes.find((type) => MediaRecorder.isTypeSupported(type)) ?? "";
}

function extensionForMimeType(mimeType) {
  if (mimeType.includes("ogg")) {
    return "ogg";
  }
  return "webm";
}

export function useRecorder() {
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  const [isRecording, setIsRecording] = useState(false);
  const [recordedFile, setRecordedFile] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recorderError, setRecorderError] = useState("");

  useEffect(() => {
    let intervalId = null;

    if (isRecording) {
      intervalId = window.setInterval(() => {
        setRecordingTime((current) => current + 1);
      }, 1000);
    }

    return () => {
      if (intervalId) {
        window.clearInterval(intervalId);
      }
    };
  }, [isRecording]);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, []);

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setRecorderError("Microphone recording is not supported in this browser.");
      return;
    }

    try {
      setRecorderError("");
      setRecordedFile(null);
      setRecordingTime(0);

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getSupportedMimeType();
      const mediaRecorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      streamRef.current = stream;
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const resolvedMimeType = mediaRecorder.mimeType || mimeType || "audio/webm";
        const extension = extensionForMimeType(resolvedMimeType);
        const blob = new Blob(chunksRef.current, { type: resolvedMimeType });
        const file = new File([blob], `recording-${Date.now()}.${extension}`, {
          type: resolvedMimeType,
        });

        setRecordedFile(file);
        setIsRecording(false);
        stopStream();
      };

      mediaRecorder.onerror = () => {
        setRecorderError("Recording failed. Please try again.");
        setIsRecording(false);
        stopStream();
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      if (error?.name === "NotAllowedError" || error?.name === "SecurityError") {
        setRecorderError("Microphone permission was denied. Please allow microphone access.");
      } else if (error?.name === "NotFoundError") {
        setRecorderError("No microphone was found on this device.");
      } else {
        setRecorderError("Unable to start recording right now.");
      }
      stopStream();
    }
  }

  function stopRecording() {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }

  function clearRecording() {
    setRecordedFile(null);
    setRecordingTime(0);
    setRecorderError("");
  }

  function stopStream() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    mediaRecorderRef.current = null;
  }

  return {
    isRecording,
    recordedFile,
    recordingTime,
    recorderError,
    startRecording,
    stopRecording,
    clearRecording,
  };
}
