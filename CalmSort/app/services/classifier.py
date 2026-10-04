import re
from pathlib import Path

from app.core.classification import (
    CONTENT_CATEGORIES,
    CONTENT_EXTENSIONS,
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
CONTENT_SCORE = 15


class FileClassifier:
    def classify(
        self,
        file_info: FileInfo,
    ) -> ClassificationResult:
        type_scores: dict[str, float] = {
            "Documents": 0,
            "Images": 0,
            "Videos": 0,
            "Music": 0,
            "Archives": 0,
        }

        context_scores: dict[str, float] = {
            "College": 0,
            "Work": 0,
            "Personal": 0,
        }

        reasons: list[ClassificationReason] = []

        self._score_extension(
            file_info,
            type_scores,
            reasons,
        )

        self._score_filename(
            file_info,
            context_scores,
            reasons,
        )

        self._score_context(
            file_info,
            context_scores,
            reasons,
        )

        self._score_content(
            file_info,
            context_scores,
            reasons,
        )

        file_type = self._get_file_type(type_scores)

        (
            context,
            context_score,
            second_context_score,
        ) = self._get_context(context_scores)

        if context is not None:
            category = context
            confidence = context_score
            margin = context_score - second_context_score
        else:
            category = file_type
            confidence = type_scores.get(
                file_type,
                0,
            )

            margin = self._get_type_margin(
                type_scores,
                file_type,
            )

        decision = self._make_decision(
            confidence,
            margin,
        )

        return ClassificationResult(
            category=category,
            confidence=confidence,
            margin=margin,
            decision=decision,
            reasons=reasons,
            file_type=file_type,
            context=context,
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
                            f"{extension} is a "
                            f"{category.lower()} file type"
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
        filename = Path(
            file_info.name
        ).stem.lower()

        words = set(
            filename.replace("-", " ")
            .replace("_", " ")
            .replace(".", " ")
            .split()
        )

        for category, keywords in KEYWORD_CATEGORIES.items():
            matched_keywords = words.intersection(
                keywords
            )

            for keyword in matched_keywords:
                scores[category] += KEYWORD_SCORE

                reasons.append(
                    ClassificationReason(
                        signal="keyword",
                        description=(
                            f'"{keyword}" '
                            "found in filename"
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
        path = file_info.path

        # Absolute paths can contain unrelated folders such as
        # temporary pytest directories. We only use folder
        # context when the supplied path is relative.
        if path.is_absolute():
            return

        path_parts: set[str] = set()

        for part in path.parts[:-1]:
            words = (
                part.lower()
                .replace("-", " ")
                .replace("_", " ")
                .replace(".", " ")
                .split()
            )

            path_parts.update(words)

        for category, keywords in CONTEXT_CATEGORIES.items():
            matched_keywords = path_parts.intersection(
                keywords
            )

            for keyword in matched_keywords:
                scores[category] += CONTEXT_SCORE

                reasons.append(
                    ClassificationReason(
                        signal="context",
                        description=(
                            f'"{keyword}" '
                            "found in folder path"
                        ),
                        score=CONTEXT_SCORE,
                    )
                )

    def _score_content(
        self,
        file_info: FileInfo,
        scores: dict[str, float],
        reasons: list[ClassificationReason],
    ) -> None:
        extension = file_info.extension.lower()

        if extension not in CONTENT_EXTENSIONS:
            return

        try:
            content = file_info.path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()
        except (OSError, UnicodeError):
            return

        for category, keywords in CONTENT_CATEGORIES.items():
            matched_keywords = [
                keyword
                for keyword in sorted(keywords)
                if re.search(
                    rf"(?<!\w){re.escape(keyword)}(?!\w)",
                    content,
                )
            ]

            if not matched_keywords:
                continue

            scores[category] += CONTENT_SCORE

            reasons.append(
                ClassificationReason(
                    signal="content",
                    description=(
                        f'content contains '
                        f'"{matched_keywords[0]}"'
                    ),
                    score=CONTENT_SCORE,
                )
            )

    def _get_file_type(
        self,
        scores: dict[str, float],
    ) -> str:
        return max(
            scores,
            key=scores.get,
        )

    def _get_context(
        self,
        scores: dict[str, float],
    ) -> tuple[str | None, float, float]:
        ranked_contexts = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_context, best_score = ranked_contexts[0]
        second_score = ranked_contexts[1][1]

        if best_score <= 0:
            return None, 0, second_score

        return (
            best_context,
            best_score,
            second_score,
        )

    def _get_type_margin(
        self,
        scores: dict[str, float],
        best_type: str,
    ) -> float:
        other_scores = [
            score
            for category, score in scores.items()
            if category != best_type
        ]

        second_score = max(
            other_scores,
            default=0,
        )

        return scores[best_type] - second_score

    def _make_decision(
        self,
        confidence: float,
        margin: float,
    ) -> str:
        if confidence >= 70 and margin >= 15:
            return "AUTO"

        return "REVIEW"