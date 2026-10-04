from datetime import datetime
from pathlib import Path

from app.core.models import (
    ClassificationReason,
    ClassificationResult,
    FileInfo,
)


def test_file_info_creation():
    now = datetime.now()

    file_info = FileInfo(
        name="example.pdf",
        path=Path("example.pdf"),
        extension=".pdf",
        size=1024,
        created_at=now,
        modified_at=now,
    )

    assert file_info.name == "example.pdf"
    assert file_info.extension == ".pdf"
    assert file_info.size == 1024
    assert file_info.path == Path("example.pdf")


def test_classification_reason_creation():
    reason = ClassificationReason(
        signal="keyword",
        description='"assignment" found in filename',
        score=25,
    )

    assert reason.signal == "keyword"
    assert reason.description == '"assignment" found in filename'
    assert reason.score == 25


def test_classification_result_creation():
    reason = ClassificationReason(
        signal="keyword",
        description='"assignment" found in filename',
        score=25,
    )

    result = ClassificationResult(
        category="College",
        confidence=94.0,
        margin=51.0,
        decision="AUTO",
        reasons=[reason],
    )

    assert result.category == "College"
    assert result.confidence == 94.0
    assert result.margin == 51.0
    assert result.decision == "AUTO"
    assert len(result.reasons) == 1