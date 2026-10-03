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
        Path("College") / "Semester 5" / "DBMS" / "chapter1.pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "College"
    assert result.confidence == 90
    assert result.margin == 70
    assert result.decision == "AUTO"


def test_work_folder_context():
    classifier = FileClassifier()

    file_info = create_file_info(
        "document.pdf",
        ".pdf",
        Path("Work") / "Client A" / "document.pdf",
    )

    result = classifier.classify(file_info)

    assert result.category == "Work"
    assert result.confidence == 60
    assert result.margin == 40
    assert result.decision == "REVIEW"


def test_personal_folder_context():
    classifier = FileClassifier()

    file_info = create_file_info(
        "photo.jpg",
        ".jpg",
        Path("Personal") / "Travel" / "photo.jpg",
    )

    result = classifier.classify(file_info)

    assert result.category == "Personal"
    assert result.confidence == 60
    assert result.margin == 40
    assert result.decision == "REVIEW"


def test_context_reason_is_recorded():
    classifier = FileClassifier()

    file_info = create_file_info(
        "chapter1.pdf",
        ".pdf",
        Path("College") / "DBMS" / "chapter1.pdf",
    )

    result = classifier.classify(file_info)

    descriptions = [
        reason.description
        for reason in result.reasons
    ]

    assert '"college" found in folder path' in descriptions
    assert '"dbms" found in folder path' in descriptions