from pathlib import Path

import pytest

from app.services.file_scanner import FileScanner


def test_valid_folder(tmp_path: Path):
    scanner = FileScanner(tmp_path)

    scanner.validate_folder()


def test_missing_folder():
    scanner = FileScanner(Path("this-folder-does-not-exist"))

    with pytest.raises(FileNotFoundError):
        scanner.validate_folder()


def test_get_files(tmp_path: Path):
    (tmp_path / "resume.pdf").touch()
    (tmp_path / "photo.jpg").touch()
    (tmp_path / "folder").mkdir()

    scanner = FileScanner(tmp_path)

    files = scanner.get_files()

    assert len(files) == 2
    assert tmp_path / "resume.pdf" in files
    assert tmp_path / "photo.jpg" in files
    assert tmp_path / "folder" not in files


def test_get_file_info(tmp_path: Path):
    test_file = tmp_path / "Resume.PDF"
    test_file.write_text("CalmSort test file")

    scanner = FileScanner(tmp_path)

    file_info = scanner.get_file_info(test_file)

    assert file_info.name == "Resume.PDF"
    assert file_info.path == test_file
    assert file_info.extension == ".pdf"
    assert file_info.size > 0
    assert file_info.created_at is not None
    assert file_info.modified_at is not None


def test_scan(tmp_path: Path):
    (tmp_path / "document.pdf").write_text("PDF content")
    (tmp_path / "photo.jpg").write_text("Image content")
    (tmp_path / "notes.txt").write_text("Notes")
    (tmp_path / "subfolder").mkdir()

    scanner = FileScanner(tmp_path)

    results = scanner.scan()

    assert len(results) == 3

    names = {file_info.name for file_info in results}

    assert names == {
        "document.pdf",
        "photo.jpg",
        "notes.txt",
    }


def test_scan_continues_after_file_error(tmp_path: Path, monkeypatch):
    good_file = tmp_path / "good.txt"
    bad_file = tmp_path / "bad.txt"

    good_file.write_text("Good file")
    bad_file.write_text("Bad file")

    scanner = FileScanner(tmp_path)

    original_get_file_info = scanner.get_file_info

    def mock_get_file_info(file_path: Path):
        if file_path == bad_file:
            raise OSError("Permission denied")

        return original_get_file_info(file_path)

    monkeypatch.setattr(
        scanner,
        "get_file_info",
        mock_get_file_info,
    )

    results = scanner.scan()

    assert len(results) == 1
    assert results[0].name == "good.txt"

    assert len(scanner.errors) == 1
    assert "bad.txt" in scanner.errors[0]
    assert "Permission denied" in scanner.errors[0]