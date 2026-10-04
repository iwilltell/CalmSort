from datetime import datetime
from pathlib import Path
import shutil

from app.core.models import (
    ClassificationResult,
    FileInfo,
    MoveRecord,
    OrganizationAction,
)


class FileOrganizer:
    def plan(
        self,
        file_info: FileInfo,
        classification: ClassificationResult,
    ) -> OrganizationAction:
        destination_folder = (
            file_info.path.parent
            / classification.category
        )

        destination = (
            destination_folder
            / file_info.name
        )

        return OrganizationAction(
            source=file_info.path,
            destination=destination,
            category=classification.category,
            decision=classification.decision,
        )

    def execute(
        self,
        action: OrganizationAction,
    ) -> MoveRecord:
        if action.decision != "AUTO":
            raise ValueError(
                "Only AUTO actions can be executed."
            )

        source = action.source
        destination = action.destination

        if not source.exists():
            raise FileNotFoundError(
                f"Source file does not exist: {source}"
            )

        if not source.is_file():
            raise ValueError(
                f"Source path is not a file: {source}"
            )

        if source.resolve() == destination.resolve():
            raise ValueError(
                "Source and destination are the same file."
            )

        destination = self._get_available_destination(
            destination
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(source),
            str(destination),
        )

        return MoveRecord(
            source=source,
            destination=destination,
            category=action.category,
            moved_at=datetime.now(),
        )

    def undo(
        self,
        record: MoveRecord,
    ) -> Path:
        source = record.source
        destination = record.destination

        if not destination.exists():
            raise FileNotFoundError(
                f"Moved file does not exist: {destination}"
            )

        if not destination.is_file():
            raise ValueError(
                f"Moved path is not a file: {destination}"
            )

        if source.exists():
            raise FileExistsError(
                f"Original location already exists: {source}"
            )

        source.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(destination),
            str(source),
        )

        return source

    def _get_available_destination(
        self,
        destination: Path,
    ) -> Path:
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent

        counter = 1

        while True:
            candidate = (
                parent
                / f"{stem} ({counter}){suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1