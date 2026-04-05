from __future__ import annotations

from threading import Lock
from uuid import uuid4

from app.models.speech import PhonemeWordAnalysis


class PronunciationScoringService:
    def compute_overall_similarity(
        self,
        text_similarity: float,
        phoneme_similarity: float,
    ) -> float:
        return round((phoneme_similarity * 0.7) + (text_similarity * 0.3), 4)

    def compute_pronunciation_score(
        self,
        text_similarity: float,
        phoneme_similarity: float,
    ) -> int:
        return round(self.compute_overall_similarity(text_similarity, phoneme_similarity) * 100)

    def classify_grade(self, pronunciation_score: int) -> str:
        if pronunciation_score >= 90:
            return "Excellent"
        if pronunciation_score >= 75:
            return "Good"
        if pronunciation_score >= 50:
            return "Needs Improvement"
        return "Poor"

    def build_actionable_feedback(
        self,
        base_feedback: str,
        phoneme_analysis: list[PhonemeWordAnalysis],
    ) -> str:
        issue_summaries = self._collect_issue_summaries(phoneme_analysis)
        suggestion = self._build_suggestion(phoneme_analysis)

        parts = [base_feedback]
        if issue_summaries and issue_summaries not in base_feedback:
            parts.append(issue_summaries)
        if suggestion:
            parts.append(suggestion)
        return " ".join(parts)

    def _collect_issue_summaries(
        self,
        phoneme_analysis: list[PhonemeWordAnalysis],
    ) -> str:
        summaries: list[str] = []

        for word_analysis in phoneme_analysis:
            for issue in word_analysis.issues:
                if issue.issue_type == "missing" and issue.expected_phoneme:
                    summaries.append(f"you missed the '{self._sound_label(issue.expected_phoneme)}' sound")
                elif issue.issue_type == "extra" and issue.actual_phoneme:
                    summaries.append(f"you added an extra '{self._sound_label(issue.actual_phoneme)}' sound")
                elif (
                    issue.issue_type == "substitution"
                    and issue.expected_phoneme
                    and issue.actual_phoneme
                ):
                    summaries.append(
                        f"you replaced '{self._sound_label(issue.expected_phoneme)}' with "
                        f"'{self._sound_label(issue.actual_phoneme)}'"
                    )

                if len(summaries) == 2:
                    break
            if len(summaries) == 2:
                break

        if not summaries:
            return ""
        if len(summaries) == 1:
            return summaries[0][:1].upper() + summaries[0][1:] + "."
        return summaries[0][:1].upper() + summaries[0][1:] + f" and {summaries[1]}."

    def _build_suggestion(self, phoneme_analysis: list[PhonemeWordAnalysis]) -> str:
        for word_analysis in phoneme_analysis:
            for issue in word_analysis.issues:
                if issue.issue_type == "missing":
                    return "Try slowing down and emphasizing the missing consonant sound."
                if issue.issue_type == "substitution":
                    return "Try practicing in front of a mirror and focus on mouth shape for the starting sound."
                if issue.issue_type == "extra":
                    return "Try speaking a little more slowly to avoid adding extra sounds."
        return "Keep practicing with short repetitions and listen closely to the target pronunciation."

    def _sound_label(self, phoneme: str) -> str:
        return phoneme.lower()


class SessionAttemptTracker:
    def __init__(self) -> None:
        self._store: dict[str, list[int]] = {}
        self._lock = Lock()

    def get_or_create_session_id(self, session_id: str | None) -> str:
        if session_id and session_id.strip():
            return session_id.strip()
        return str(uuid4())

    def record_attempt(self, session_id: str, score: int) -> dict:
        with self._lock:
            history = self._store.setdefault(session_id, [])
            history.append(score)
            return {
                "attempts": len(history),
                "previous_scores": history.copy(),
            }


scoring_service = PronunciationScoringService()
attempt_tracker = SessionAttemptTracker()
