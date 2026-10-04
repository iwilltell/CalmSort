from datetime import datetime
from pathlib import Path
import shutil

import pytest

from app.core.models import (
    ClassificationResult,
    FileInfo,
    MoveRecord,
)
from app.services.organizer import FileOrganizer


def create_file_info(
    path: Path,
) -> FileInfo:
    now = datetime.now()

    return FileInfo(
        name=path.name,
        path=path,
        extension=path.suffix.lower(),
        size=1024,
        created_at=now,
        modified_at=now,
    )


def create_classification(
    category: str,
    decision: str = "AUTO",
) -> ClassificationResult:
    return ClassificationResult(
        category=category,
        confidence=90,
        margin=70,
        decision=decision,
        reasons=[],
        file_type="Documents",
        context=category,
    )


def test_plan_college_destination(tmp_path: Path):
    source = (
        tmp_path
        / "Downloads"
        / "DBMS_Assignment.pdf"
    )

    source.parent.mkdir()

    source.write_text(
        "CalmSort test file",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    assert action.source == source

    assert action.destination == (
        tmp_path
        / "Downloads"
        / "College"
        / "DBMS_Assignment.pdf"
    )

    assert action.category == "College"
    assert action.decision == "AUTO"


def test_plan_does_not_move_file(tmp_path: Path):
    source = (
        tmp_path
        / "Downloads"
        / "photo.jpg"
    )

    source.parent.mkdir()

    source.write_text(
        "CalmSort test file",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "Images",
        decision="REVIEW",
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    assert source.exists()
    assert not action.destination.exists()


def test_execute_moves_file(tmp_path: Path):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    source.parent.mkdir()

    source.write_text(
        "CalmSort test file",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    expected_destination = (
        tmp_path
        / "Downloads"
        / "College"
        / "assignment.pdf"
    )

    assert isinstance(record, MoveRecord)
    assert record.source == source
    assert record.destination == expected_destination
    assert record.category == "College"

    assert not source.exists()
    assert expected_destination.exists()

    assert expected_destination.read_text(
        encoding="utf-8"
    ) == "CalmSort test file"


def test_execute_refuses_review_action(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "document.pdf"
    )

    source.parent.mkdir()

    source.write_text(
        "CalmSort test file",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "Documents",
        decision="REVIEW",
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    with pytest.raises(ValueError):
        organizer.execute(action)

    assert source.exists()


def test_execute_resolves_first_collision(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    destination_folder = (
        tmp_path
        / "Downloads"
        / "College"
    )

    destination = (
        destination_folder
        / "assignment.pdf"
    )

    source.parent.mkdir()
    destination_folder.mkdir()

    source.write_text(
        "New assignment",
        encoding="utf-8",
    )

    destination.write_text(
        "Existing assignment",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    expected_destination = (
        destination_folder
        / "assignment (1).pdf"
    )

    assert record.destination == expected_destination
    assert expected_destination.exists()
    assert destination.exists()

    assert destination.read_text(
        encoding="utf-8"
    ) == "Existing assignment"

    assert expected_destination.read_text(
        encoding="utf-8"
    ) == "New assignment"

    assert not source.exists()


def test_execute_resolves_multiple_collisions(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    destination_folder = (
        tmp_path
        / "Downloads"
        / "College"
    )

    destination_folder.mkdir(
        parents=True
    )

    source.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source.write_text(
        "New assignment",
        encoding="utf-8",
    )

    (
        destination_folder
        / "assignment.pdf"
    ).write_text(
        "Existing 1",
        encoding="utf-8",
    )

    (
        destination_folder
        / "assignment (1).pdf"
    ).write_text(
        "Existing 2",
        encoding="utf-8",
    )

    (
        destination_folder
        / "assignment (2).pdf"
    ).write_text(
        "Existing 3",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    expected_destination = (
        destination_folder
        / "assignment (3).pdf"
    )

    assert record.destination == expected_destination
    assert expected_destination.exists()

    assert not source.exists()

    assert (
        destination_folder
        / "assignment.pdf"
    ).read_text(
        encoding="utf-8"
    ) == "Existing 1"

    assert (
        destination_folder
        / "assignment (1).pdf"
    ).read_text(
        encoding="utf-8"
    ) == "Existing 2"

    assert (
        destination_folder
        / "assignment (2).pdf"
    ).read_text(
        encoding="utf-8"
    ) == "Existing 3"

    assert expected_destination.read_text(
        encoding="utf-8"
    ) == "New assignment"


def test_execute_refuses_missing_source(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "missing.pdf"
    )

    file_info = FileInfo(
        name="missing.pdf",
        path=source,
        extension=".pdf",
        size=0,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )

    classification = create_classification(
        "Documents"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    with pytest.raises(FileNotFoundError):
        organizer.execute(action)


def test_execute_refuses_directory_source(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "folder"
    )

    source.mkdir(parents=True)

    file_info = FileInfo(
        name="folder",
        path=source,
        extension="",
        size=0,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )

    classification = create_classification(
        "Documents"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    with pytest.raises(ValueError):
        organizer.execute(action)

    assert source.exists()
    assert source.is_dir()


def test_undo_moves_file_back(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    source.parent.mkdir()

    source.write_text(
        "Original assignment",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    restored_path = organizer.undo(record)

    assert restored_path == source

    assert source.exists()
    assert not record.destination.exists()

    assert source.read_text(
        encoding="utf-8"
    ) == "Original assignment"


def test_undo_creates_original_parent_folder(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "Projects"
        / "assignment.pdf"
    )

    source.parent.mkdir(
        parents=True
    )

    source.write_text(
        "Original assignment",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    destination = record.destination

    backup_destination = (
        tmp_path
        / "assignment_backup.pdf"
    )

    shutil.move(
        str(destination),
        str(backup_destination),
    )

    record = MoveRecord(
        source=record.source,
        destination=backup_destination,
        category=record.category,
        moved_at=record.moved_at,
    )

    shutil.rmtree(source.parent)

    restored_path = organizer.undo(record)

    assert restored_path == source
    assert source.exists()

    assert source.read_text(
        encoding="utf-8"
    ) == "Original assignment"


def test_undo_refuses_existing_original(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    source.parent.mkdir()

    source.write_text(
        "Original assignment",
        encoding="utf-8",
    )

    file_info = create_file_info(source)

    classification = create_classification(
        "College"
    )

    organizer = FileOrganizer()

    action = organizer.plan(
        file_info,
        classification,
    )

    record = organizer.execute(action)

    source.write_text(
        "New file created later",
        encoding="utf-8",
    )

    with pytest.raises(FileExistsError):
        organizer.undo(record)

    assert source.exists()
    assert record.destination.exists()

    assert source.read_text(
        encoding="utf-8"
    ) == "New file created later"


def test_undo_refuses_missing_moved_file(
    tmp_path: Path,
):
    source = (
        tmp_path
        / "Downloads"
        / "assignment.pdf"
    )

    destination = (
        tmp_path
        / "Downloads"
        / "College"
        / "assignment.pdf"
    )

    record = MoveRecord(
        source=source,
        destination=destination,
        category="College",
        moved_at=datetime.now(),
    )

    organizer = FileOrganizer()

    with pytest.raises(FileNotFoundError):
        organizer.undo(record)