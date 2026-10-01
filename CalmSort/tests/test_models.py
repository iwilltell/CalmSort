from datetime import datetime
from pathlib import Path

from app.core.models import FileInfo


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