from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    name: str = "CalmSort"
    version: str = "0.1.0"
    confidence_threshold: float = 0.70
    data_dir: Path = Path("data")

    @property
    def database_path(self) -> Path:
        return self.data_dir / "calmsort.db"


CONFIG = AppConfig()
