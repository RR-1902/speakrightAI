from __future__ import annotations

import re
from difflib import SequenceMatcher

from app.models.speech import PhonemeWordAnalysis, WordDifference
from app.services.phoneme import phoneme_service
from app.services.scoring import scoring_service

PUNCTUATION_PATTERN = re.compile(r"[^\w\s]")
WHITESPACE_PATTERN = re.compile(r"\s+")


class PronunciationComparisonService:
    """Compares transcribed speech with expected text.

    The implementation is intentionally text-based for Phase 2 so it can later
    be extended with phoneme-aware logic without changing the route contract.
    """

    def normalize_text(self, text: str) -> str:
        cleaned = PUNCTUATION_PATTERN.sub("", text.lower()).strip()
        return WHITESPACE_PATTERN.sub(" ", cleaned)

    def compute_similarity(self, expected_text: str, spoken_text: str) -> float:
        normalized_expected = self.normalize_text(expected_text)
        normalized_spoken = self.normalize_text(spoken_text)

        if not normalized_expected and not normalized_spoken:
            return 1.0
        if not normalized_expected or not normalized_spoken:
            return 0.0

        return round(
            SequenceMatcher(None, normalized_expected, normalized_spoken).ratio(),
            4,
        )

    def get_word_differences(
        self,
        expected_text: str,
        spoken_text: str,
    ) -> list[WordDifference]:
        expected_words = self.normalize_text(expected_text).split()
        spoken_words = self.normalize_text(spoken_text).split()
        matcher = SequenceMatcher(None, expected_words, spoken_words)
        differences: list[WordDifference] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            expected_chunk = expected_words[i1:i2]
            spoken_chunk = spoken_words[j1:j2]
            max_len = max(len(expected_chunk), len(spoken_chunk))

            for index in range(max_len):
                differences.append(
                    WordDifference(
                        expected=expected_chunk[index] if index < len(expected_chunk) else None,
                        spoken=spoken_chunk[index] if index < len(spoken_chunk) else None,
                    )
                )

        return differences

    def generate_feedback(
        self,
        expected_text: str,
        spoken_text: str,
        similarity_score: float,
        phoneme_analysis: list[PhonemeWordAnalysis],
    ) -> str:
        phoneme_hint = self._build_phoneme_hint(phoneme_analysis)

        if similarity_score > 0.9:
            if phoneme_hint:
                return (
                    "Excellent pronunciation. Your speech closely matches the expected text. "
                    f"{phoneme_hint}"
                )
            return "Excellent pronunciation. Your speech closely matches the expected text."
        if similarity_score >= 0.6:
            if phoneme_hint:
                return f"Good attempt. Minor pronunciation differences detected. {phoneme_hint}"
            return "Good attempt. Minor pronunciation differences detected."

        base_feedback = (
            f"You said '{spoken_text}', but expected '{expected_text}'. "
            "Practice the correct pronunciation."
        )
        if phoneme_hint:
            return f"{base_feedback} {phoneme_hint}"
        return base_feedback

    def _build_phoneme_hint(
        self,
        phoneme_analysis: list[PhonemeWordAnalysis],
    ) -> str | None:
        for word_analysis in phoneme_analysis:
            for issue in word_analysis.issues:
                if issue.issue_type in {"missing", "extra", "substitution"}:
                    return issue.message
        return None

    def compare(self, expected_text: str, spoken_text: str) -> dict:
        text_similarity = self.compute_similarity(expected_text, spoken_text)
        phoneme_analysis = phoneme_service.compare_text(expected_text, spoken_text)
        phoneme_similarity = phoneme_service.compute_phoneme_similarity(
            expected_text,
            spoken_text,
        )
        similarity_score = scoring_service.compute_overall_similarity(
            text_similarity=text_similarity,
            phoneme_similarity=phoneme_similarity,
        )
        pronunciation_score = scoring_service.compute_pronunciation_score(
            text_similarity=text_similarity,
            phoneme_similarity=phoneme_similarity,
        )
        grade = scoring_service.classify_grade(pronunciation_score)
        base_feedback = self.generate_feedback(
            expected_text=expected_text,
            spoken_text=spoken_text,
            similarity_score=similarity_score,
            phoneme_analysis=phoneme_analysis,
        )

        return {
            "expected_text": expected_text,
            "transcribed_text": spoken_text,
            "similarity_score": similarity_score,
            "pronunciation_score": pronunciation_score,
            "grade": grade,
            "feedback": scoring_service.build_actionable_feedback(
                base_feedback=base_feedback,
                phoneme_analysis=phoneme_analysis,
            ),
            "word_differences": self.get_word_differences(expected_text, spoken_text),
            "phoneme_analysis": phoneme_analysis,
        }


comparison_service = PronunciationComparisonService()
