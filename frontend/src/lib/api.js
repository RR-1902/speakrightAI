const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function submitPronunciation({ expectedText, sessionId, file }) {
  const formData = new FormData();
  formData.append("expected_text", expectedText);

  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  if (file) {
    formData.append("file", file);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/speech/transcribe`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      "Something went wrong while analyzing your pronunciation.";
    throw new Error(message);
  }

  return data;
}
