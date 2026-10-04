from datetime import datetime
from pathlib import Path

from app.core.models import FileInfo
from app.services.classifier import FileClassifier


def create_file_info(
    name: str,
    extension: str,
    path: Path | None = None,
) -> FileInfo:
    now = datetime.now()

    if path is None:
        path = Path(name)

    return FileInfo(
        name=name,
        path=path,
        extension=extension,
        size=1024,
        created_at=now,
        modified_at=now,
    )


def test_pdf_document_classification():
    classifier = FileClassifier()

    file_info = create_file_info(
        "document.pdf",
        ".pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "Documents"
    assert result.file_type == "Documents"
    assert result.context is None
    assert result.confidence == 20
    assert result.decision == "REVIEW"


def test_college_assignment_classification():
    classifier = FileClassifier()

    file_info = create_file_info(
        "DBMS_Assignment.pdf",
        ".pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "College"
    assert result.file_type == "Documents"
    assert result.context == "College"
    assert result.confidence == 70
    assert result.decision == "AUTO"


def test_work_invoice_classification():
    classifier = FileClassifier()

    file_info = create_file_info(
        "client_invoice.pdf",
        ".pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "Work"
    assert result.file_type == "Documents"
    assert result.context == "Work"
    assert result.confidence == 70
    assert result.decision == "AUTO"


def test_image_classification():
    classifier = FileClassifier()

    file_info = create_file_info(
        "holiday_photo.jpg",
        ".jpg",
    )

    result = classifier.classify(file_info)

    assert result.category == "Images"
    assert result.file_type == "Images"
    assert result.context is None
    assert result.confidence == 20
    assert result.decision == "REVIEW"


def test_keyword_reason_is_recorded():
    classifier = FileClassifier()

    file_info = create_file_info(
        "DBMS_Assignment.pdf",
        ".pdf",
    )

    result = classifier.classify(file_info)

    descriptions = [
        reason.description
        for reason in result.reasons
    ]

    assert '"dbms" found in filename' in descriptions
    assert '"assignment" found in filename' in descriptions


def test_extension_reason_is_recorded():
    classifier = FileClassifier()

    file_info = create_file_info(
        "photo.jpg",
        ".jpg",
    )

    result = classifier.classify(file_info)

    assert len(result.reasons) == 1
    assert result.reasons[0].signal == "extension"
    assert result.reasons[0].score == 20


def test_college_folder_context():
    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter1.pdf",
        ".pdf",
        Path("College")
        / "Semester 5"
        / "DBMS"
        / "chapter1.pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "College"
    assert result.file_type == "Documents"
    assert result.context == "College"
    assert result.confidence == 90
    assert result.margin == 90
    assert result.decision == "AUTO"


def test_work_folder_context():
    classifier = FileClassifier()

    file_info = create_file_info(
        "document.pdf",
        ".pdf",
        Path("Work")
        / "Client A"
        / "document.pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "Work"
    assert result.file_type == "Documents"
    assert result.context == "Work"
    assert result.confidence == 60
    assert result.margin == 60
    assert result.decision == "REVIEW"


def test_personal_folder_context():
    classifier = FileClassifier()

    file_info = create_file_info(
        "photo.jpg",
        ".jpg",
        Path("Personal")
        / "Travel"
        / "photo.jpg",
    )

    result = classifier.classify(file_info)

    assert result.category == "Personal"
    assert result.file_type == "Images"
    assert result.context == "Personal"
    assert result.confidence == 60
    assert result.margin == 60
    assert result.decision == "REVIEW"


def test_context_reason_is_recorded():
    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter1.pdf",
        ".pdf",
        Path("College")
        / "DBMS"
        / "chapter1.pdf",
    )

    result = classifier.classify(file_info)

    descriptions = [
        reason.description
        for reason in result.reasons
    ]

    assert '"college" found in folder path' in descriptions
    assert '"dbms" found in folder path' in descriptions


def test_college_content_classification(tmp_path: Path):
    test_file = tmp_path / "chapter.txt"

    test_file.write_text(
        "This lecture discusses DBMS, "
        "normalization, and database transactions.",
        encoding="utf-8",
    )

    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter.txt",
        ".txt",
        test_file,
    )

    result = classifier.classify(file_info)

    assert result.category == "College"
    assert result.file_type == "Documents"
    assert result.context == "College"
    assert result.confidence == 15
    assert result.margin == 15
    assert result.decision == "REVIEW"


def test_work_content_classification(tmp_path: Path):
    test_file = tmp_path / "notes.txt"

    test_file.write_text(
        "The client meeting discussed the project "
        "deadline and final report.",
        encoding="utf-8",
    )

    classifier = FileClassifier()

    file_info = create_file_info(
        "notes.txt",
        ".txt",
        test_file,
    )

    result = classifier.classify(file_info)

    assert result.category == "Work"
    assert result.file_type == "Documents"
    assert result.context == "Work"
    assert result.confidence == 15
    assert result.margin == 15
    assert result.decision == "REVIEW"


def test_content_reason_is_recorded(tmp_path: Path):
    test_file = tmp_path / "chapter.txt"

    test_file.write_text(
        "This lecture explains DBMS concepts.",
        encoding="utf-8",
    )

    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter.txt",
        ".txt",
        test_file,
    )

    result = classifier.classify(file_info)

    content_reasons = [
        reason
        for reason in result.reasons
        if reason.signal == "content"
    ]

    assert len(content_reasons) == 1
    assert content_reasons[0].score == 15
    assert "content contains" in content_reasons[0].description


def test_content_score_is_only_applied_once_per_category(
    tmp_path: Path,
):
    test_file = tmp_path / "chapter.txt"

    test_file.write_text(
        """
        DBMS
        assignment
        semester
        lecture
        notes
        university
        college
        """,
        encoding="utf-8",
    )

    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter.txt",
        ".txt",
        test_file,
    )

    result = classifier.classify(file_info)

    assert result.category == "College"
    assert result.file_type == "Documents"
    assert result.context == "College"
    assert result.confidence == 15

    content_reasons = [
        reason
        for reason in result.reasons
        if reason.signal == "content"
    ]

    assert len(content_reasons) == 1