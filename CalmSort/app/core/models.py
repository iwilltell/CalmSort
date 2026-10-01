from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileInfo:
    name: str
    path: Path
    extension: str
    size: int
    created_at: datetime
    modified_at: datetime