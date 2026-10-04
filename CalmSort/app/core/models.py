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


@dataclass
class ClassificationReason:
    signal: str
    description: str
    score: float


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    margin: float
    decision: str
    reasons: list[ClassificationReason]
    file_type: str = ""
    context: str | None = None


@dataclass
class OrganizationAction:
    source: Path
    destination: Path
    category: str
    decision: str


@dataclass
class MoveRecord:
    source: Path
    destination: Path
    category: str
    moved_at: datetime