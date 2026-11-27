from collections import defaultdict
import hashlib
from pathlib import Path


class DuplicateFinder:
    CHUNK_SIZE = 65536  # 64 KB chunks

    @staticmethod
    def _hash_file(file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(DuplicateFinder.CHUNK_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def find_duplicates(self, folder_path: str, recursive: bool = True) -> dict:
        target = Path(folder_path)
        if not target.exists() or not target.is_dir():
            raise ValueError("Invalid directory selected for duplicate scan.")

        size_groups = defaultdict(list)
        iterator = target.rglob("*") if recursive else target.iterdir()
        for item in iterator:
            if item.is_file() and not item.name.startswith("."):
                try:
                    size = item.stat().st_size
                    if size > 0:
                        size_groups[size].append(item)
                except OSError:
                    continue

        hash_groups = defaultdict(list)
        for size, paths in size_groups.items():
            if len(paths) < 2:
                continue
            for p in paths:
                try:
                    digest = self._hash_file(p)
                    hash_groups[(size, digest)].append(p)
                except OSError:
                    continue

        duplicate_groups = []
        recoverable_bytes = 0
        for (size, digest), paths in hash_groups.items():
            if len(paths) > 1:
                sorted_paths = sorted(paths, key=lambda p: (len(str(p)), p.name))
                duplicate_groups.append({
                    "hash": digest[:12],
                    "size_bytes": size,
                    "files": [str(p) for p in sorted_paths]
                })
                recoverable_bytes += size * (len(sorted_paths) - 1)

        return {
            "groups": duplicate_groups,
            "group_count": len(duplicate_groups),
            "recoverable_bytes": recoverable_bytes
        }

    @staticmethod
    def format_size(num_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if num_bytes < 1024.0:
                return f"{num_bytes:.2f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.2f} PB"

    @staticmethod
    def delete_files(file_paths: list[str]) -> int:
        deleted = 0
        for fp in file_paths:
            p = Path(fp)
            try:
                if p.exists() and p.is_file():
                    p.unlink()
                    deleted += 1
            except OSError:
                continue
        return deleted
