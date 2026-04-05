from __future__ import annotations

import re
from difflib import SequenceMatcher

import nltk
from nltk.corpus import cmudict

from app.models.speech import PhonemeIssue, PhonemeWordAnalysis

WORD_PATTERN = re.compile(r"[a-zA-Z']+")
STRESS_PATTERN = re.compile(r"\d")

DIGRAPH_TO_PHONEME = {
    "ch": "CH",
    "ck": "K",
    "ee": "IY",
    "oo": "UW",
    "ou": "AW",
    "ow": "AW",
    "ph": "F",
    "qu": "KW",
    "sh": "SH",
    "th": "TH",
}

LETTER_TO_PHONEME = {
    "a": "AH",
    "b": "B",
    "c": "K",
    "d": "D",
    "e": "EH",
    "f": "F",
    "g": "G",
    "h": "HH",
    "i": "IH",
    "j": "JH",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "OW",
    "p": "P",
    "q": "K",
    "r": "R",
    "s": "S",
    "t": "T",
    "u": "UH",
    "v": "V",
    "w": "W",
    "x": "KS",
    "y": "Y",
    "z": "Z",
}

PHONEME_TO_SOUND = {
    "AE": "a",
    "AH": "uh",
    "AW": "ow",
    "B": "b",
    "CH": "ch",
    "D": "d",
    "EH": "eh",
    "ER": "er",
    "F": "f",
    "G": "g",
    "HH": "h",
    "IH": "i",
    "IY": "ee",
    "JH": "j",
    "K": "k",
    "KS": "x",
    "KW": "qu",
    "L": "l",
    "M": "m",
    "N": "n",
    "OW": "o",
    "P": "p",
    "R": "r",
    "S": "s",
    "SH": "sh",
    "T": "t",
    "TH": "th",
    "UH": "u",
    "UW": "oo",
    "V": "v",
    "W": "w",
    "Y": "y",
    "Z": "z",
}


class PhonemeService:
    def __init__(self) -> None:
        self._cmu_dict: dict[str, list[list[str]]] | None = None

    def _load_cmudict(self) -> dict[str, list[list[str]]]:
        if self._cmu_dict is not None:
            return self._cmu_dict

        try:
            nltk.data.find("corpora/cmudict")
        except LookupError:
            nltk.download("cmudict", quiet=True)

        self._cmu_dict = cmudict.dict()
        return self._cmu_dict

    def tokenize(self, text: str) -> list[str]:
        return WORD_PATTERN.findall(text.lower())

    def _strip_stress(self, phonemes: list[str]) -> list[str]:
        return [STRESS_PATTERN.sub("", phoneme) for phoneme in phonemes]

    def _approximate_phonemes(self, word: str) -> list[str]:
        approximated: list[str] = []
        index = 0
        while index < len(word):
            pair = word[index : index + 2]
            if pair in DIGRAPH_TO_PHONEME:
                approximated.append(DIGRAPH_TO_PHONEME[pair])
                index += 2
                continue

            phoneme = LETTER_TO_PHONEME.get(word[index], word[index].upper())
            approximated.extend(phoneme.split())
            index += 1

        return approximated

    def word_to_phonemes(self, word: str) -> list[str]:
        normalized_word = word.lower()
        if not normalized_word:
            return []

        pronunciations = self._load_cmudict().get(normalized_word)
        if pronunciations:
            return self._strip_stress(pronunciations[0])

        return self._approximate_phonemes(normalized_word)

    def text_to_word_phonemes(self, text: str) -> list[tuple[str, list[str]]]:
        return [(word, self.word_to_phonemes(word)) for word in self.tokenize(text)]

    def flatten_phonemes(self, text: str) -> list[str]:
        flattened: list[str] = []
        for _, phonemes in self.text_to_word_phonemes(text):
            flattened.extend(phonemes)
        return flattened

    def _sound_label(self, phoneme: str | None) -> str:
        if phoneme is None:
            return "missing"
        return PHONEME_TO_SOUND.get(phoneme, phoneme.lower())

    def _build_issue_message(
        self,
        issue_type: str,
        expected_phoneme: str | None,
        actual_phoneme: str | None,
        word: str,
    ) -> str:
        if issue_type == "missing":
            return f"You missed the '{self._sound_label(expected_phoneme)}' sound in '{word}'."
        if issue_type == "extra":
            return f"You added an extra '{self._sound_label(actual_phoneme)}' sound in '{word}'."
        return (
            f"In '{word}', the '{self._sound_label(expected_phoneme)}' sound was pronounced "
            f"more like '{self._sound_label(actual_phoneme)}'."
        )

    def compare_word_phonemes(
        self,
        expected_word: str,
        spoken_word: str | None,
    ) -> PhonemeWordAnalysis | None:
        expected_phonemes = self.word_to_phonemes(expected_word)
        actual_phonemes = self.word_to_phonemes(spoken_word or "")

        matcher = SequenceMatcher(None, expected_phonemes, actual_phonemes)
        issues: list[PhonemeIssue] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            expected_chunk = expected_phonemes[i1:i2]
            actual_chunk = actual_phonemes[j1:j2]
            max_len = max(len(expected_chunk), len(actual_chunk))

            for index in range(max_len):
                expected_phoneme = expected_chunk[index] if index < len(expected_chunk) else None
                actual_phoneme = actual_chunk[index] if index < len(actual_chunk) else None

                if tag == "delete":
                    issue_type = "missing"
                elif tag == "insert":
                    issue_type = "extra"
                else:
                    issue_type = "substitution"

                issues.append(
                    PhonemeIssue(
                        issue_type=issue_type,
                        expected_phoneme=expected_phoneme,
                        actual_phoneme=actual_phoneme,
                        position=i1 + index,
                        message=self._build_issue_message(
                            issue_type=issue_type,
                            expected_phoneme=expected_phoneme,
                            actual_phoneme=actual_phoneme,
                            word=expected_word,
                        ),
                    )
                )

        if not issues:
            return None

        return PhonemeWordAnalysis(
            word=expected_word,
            spoken_word=spoken_word,
            expected_phonemes=expected_phonemes,
            actual_phonemes=actual_phonemes,
            issues=issues,
        )

    def compare_text(self, expected_text: str, spoken_text: str) -> list[PhonemeWordAnalysis]:
        expected_words = self.tokenize(expected_text)
        spoken_words = self.tokenize(spoken_text)
        matcher = SequenceMatcher(None, expected_words, spoken_words)
        analysis: list[PhonemeWordAnalysis] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            expected_chunk = expected_words[i1:i2]
            spoken_chunk = spoken_words[j1:j2]
            max_len = max(len(expected_chunk), len(spoken_chunk))

            for index in range(max_len):
                expected_word = expected_chunk[index] if index < len(expected_chunk) else None
                spoken_word = spoken_chunk[index] if index < len(spoken_chunk) else None

                if expected_word is None:
                    analysis.append(
                        PhonemeWordAnalysis(
                            word=spoken_word or "",
                            spoken_word=spoken_word,
                            expected_phonemes=[],
                            actual_phonemes=self.word_to_phonemes(spoken_word or ""),
                            issues=[
                                PhonemeIssue(
                                    issue_type="extra_word",
                                    expected_phoneme=None,
                                    actual_phoneme=None,
                                    position=None,
                                    message=f"You added the extra word '{spoken_word}'.",
                                )
                            ],
                        )
                    )
                    continue

                word_analysis = self.compare_word_phonemes(expected_word, spoken_word)
                if word_analysis is not None:
                    analysis.append(word_analysis)

        return analysis

    def compute_phoneme_similarity(self, expected_text: str, spoken_text: str) -> float:
        expected_phonemes = self.flatten_phonemes(expected_text)
        spoken_phonemes = self.flatten_phonemes(spoken_text)

        if not expected_phonemes and not spoken_phonemes:
            return 1.0
        if not expected_phonemes or not spoken_phonemes:
            return 0.0

        return round(
            SequenceMatcher(None, expected_phonemes, spoken_phonemes).ratio(),
            4,
        )


phoneme_service = PhonemeService()
