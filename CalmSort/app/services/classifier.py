from pathlib import Path

from app.core.classification import (
    CONTEXT_CATEGORIES,
    EXTENSION_CATEGORIES,
    KEYWORD_CATEGORIES,
)
from app.core.models import (
    ClassificationReason,
    ClassificationResult,
    FileInfo,
)


EXTENSION_SCORE = 20
KEYWORD_SCORE = 35
CONTEXT_SCORE = 30


class FileClassifier:
    def classify(self, file_info: FileInfo) -> ClassificationResult:
        scores: dict[str, float] = {
            "College": 0,
            "Work": 0,
            "Personal": 0,
            "Documents": 0,
            "Images": 0,
            "Videos": 0,
            "Music": 0,
            "Archives": 0,
        }

        reasons: list[ClassificationReason] = []

        self._score_extension(
            file_info,
            scores,
            reasons,
        )

        self._score_filename(
            file_info,
            scores,
            reasons,
        )

        self._score_context(
            file_info,
            scores,
            reasons,
        )

        ranked_categories = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_category, best_score = ranked_categories[0]
        second_score = ranked_categories[1][1]

        margin = best_score - second_score

        confidence = min(best_score, 100.0)

        decision = self._make_decision(
            confidence,
            margin,
        )

        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            margin=margin,
            decision=decision,
            reasons=reasons,
        )

    def _score_extension(
        self,
        file_info: FileInfo,
        scores: dict[str, float],
        reasons: list[ClassificationReason],
    ) -> None:
        extension = file_info.extension.lower()

        for category, extensions in EXTENSION_CATEGORIES.items():
            if extension in extensions:
                scores[category] += EXTENSION_SCORE

                reasons.append(
                    ClassificationReason(
                        signal="extension",
                        description=(
                            f"{extension} is a {category.lower()} "
                            "file type"
                        ),
                        score=EXTENSION_SCORE,
                    )
                )

                break

    def _score_filename(
        self,
        file_info: FileInfo,
        scores: dict[str, float],
        reasons: list[ClassificationReason],
    ) -> None:
        filename = Path(file_info.name).stem.lower()

        words = set(
            filename.replace("-", " ")
            .replace("_", " ")
            .replace(".", " ")
            .split()
        )

        for category, keywords in KEYWORD_CATEGORIES.items():
            matched_keywords = words.intersection(keywords)

            for keyword in matched_keywords:
                scores[category] += KEYWORD_SCORE

                reasons.append(
                    ClassificationReason(
                        signal="keyword",
                        description=(
                            f'"{keyword}" found in filename'
                        ),
                        score=KEYWORD_SCORE,
                    )
                )

    def _score_context(
        self,
        file_info: FileInfo,
        scores: dict[str, float],
        reasons: list[ClassificationReason],
    ) -> None:
        path_parts: set[str] = set()

        for part in file_info.path.parts[:-1]:
            words = (
                part.lower()
                .replace("-", " ")
                .replace("_", " ")
                .replace(".", " ")
                .split()
            )

            path_parts.update(words)

        for category, keywords in CONTEXT_CATEGORIES.items():
            matched_keywords = path_parts.intersection(keywords)

            for keyword in matched_keywords:
                scores[category] += CONTEXT_SCORE

                reasons.append(
                    ClassificationReason(
                        signal="context",
                        description=(
                            f'"{keyword}" found in folder path'
                        ),
                        score=CONTEXT_SCORE,
                    )
                )

    def _make_decision(
        self,
        confidence: float,
        margin: float,
    ) -> str:
        if confidence >= 70 and margin >= 15:
            return "AUTO"

        return "REVIEW"