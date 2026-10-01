from datetime import datetime
from pathlib import Path

from app.core.models import FileInfo


class FileScanner:
    def __init__(self, folder: Path):
        self.folder = folder
        self.errors: list[str] = []

    def validate_folder(self) -> None:
        if not self.folder.exists():
            raise FileNotFoundError(
                f"Folder does not exist: {self.folder}"
            )

        if not self.folder.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.folder}"
            )

    def get_files(self) -> list[Path]:
        self.validate_folder()

        return [
            item
            for item in self.folder.iterdir()
            if item.is_file()
        ]

    def get_file_info(self, file_path: Path) -> FileInfo:
        stats = file_path.stat()

        return FileInfo(
            name=file_path.name,
            path=file_path,
            extension=file_path.suffix.lower(),
            size=stats.st_size,
            created_at=datetime.fromtimestamp(stats.st_ctime),
            modified_at=datetime.fromtimestamp(stats.st_mtime),
        )

    def scan(self) -> list[FileInfo]:
        self.errors.clear()
        results: list[FileInfo] = []

        for file_path in self.get_files():
            try:
                file_info = self.get_file_info(file_path)
                results.append(file_info)
            except OSError as error:
                self.errors.append(
                    f"Could not read '{file_path}': {error}"
                )

        return results