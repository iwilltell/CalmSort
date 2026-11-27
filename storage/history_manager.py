import json
from datetime import datetime
from pathlib import Path
import shutil


DEFAULT_RULES = {
    "Documents": {
        "extensions": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"],
        "keywords": ["report", "assignment", "resume", "invoice", "notes", "syllabus"]
    },
    "Images": {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".ico"],
        "keywords": ["screenshot", "photo", "wallpaper"]
    },
    "Videos": {
        "extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "keywords": ["recording", "lecture", "video"]
    },
    "Audio": {
        "extensions": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "keywords": ["podcast", "audio", "song"]
    },
    "Code": {
        "extensions": [".py", ".java", ".c", ".cpp", ".js", ".ts", ".html", ".css", ".json", ".xml", ".sql", ".sh", ".ipynb"],
        "keywords": ["script", "source"]
    },
    "Archives": {
        "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
        "keywords": ["backup", "archive"]
    },
    "Installers": {
        "extensions": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".appimage", ".apk"],
        "keywords": ["setup", "installer"]
    }
}


class HistoryManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.rules_path = self.data_dir / "rules.json"
        self.history_path = self.data_dir / "history.json"
        self._ensure_files()

    def _ensure_files(self):
        if not self.rules_path.exists():
            self.save_rules(DEFAULT_RULES)
        if not self.history_path.exists():
            self._write_json(self.history_path, [])

    def _read_json(self, path: Path, fallback):
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return fallback

    def _write_json(self, path: Path, payload):
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

    def load_rules(self) -> dict:
        return self._read_json(self.rules_path, DEFAULT_RULES.copy())

    def save_rules(self, rules: dict):
        self._write_json(self.rules_path, rules)

    def add_or_update_rule(self, category: str, extensions: list, keywords: list):
        rules = self.load_rules()
        rules[category.strip()] = {
            "extensions": [e if e.startswith(".") else f".{e}" for e in extensions if e.strip()],
            "keywords": [k.strip() for k in keywords if k.strip()]
        }
        self.save_rules(rules)

    def delete_rule(self, category: str):
        rules = self.load_rules()
        if category in rules and category != "Others":
            del rules[category]
            self.save_rules(rules)

    def load_history(self) -> list:
        return self._read_json(self.history_path, [])

    def log_session(self, target_dir: str, moves: list, source: str = "Manual Sort") -> dict:
        history = self.load_history()
        next_id = (history[-1]["session_id"] + 1) if history else 101
        session_record = {
            "session_id": next_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_dir": str(target_dir),
            "source": source,
            "files_moved": len(moves),
            "undone": False,
            "moves": moves
        }
        history.append(session_record)
        self._write_json(self.history_path, history)
        return session_record

    def undo_session(self, session_id: int = None) -> tuple[bool, str, int]:
        history = self.load_history()
        if not history:
            return False, "No sorting sessions found in history.", 0

        target_session = None
        if session_id is None:
            for s in reversed(history):
                if not s.get("undone", False) and s.get("moves"):
                    target_session = s
                    break
        else:
            for s in history:
                if s["session_id"] == session_id:
                    target_session = s
                    break

        if not target_session:
            return False, "No active session available to undo.", 0
        if target_session.get("undone", False):
            return False, f"Session #{target_session['session_id']} was already undone.", 0

        restored = 0
        created_dirs = set()
        for move in reversed(target_session["moves"]):
            orig = Path(move["original_path"])
            curr = Path(move["new_path"])
            if curr.exists():
                orig.parent.mkdir(parents=True, exist_ok=True)
                dest = orig
                counter = 1
                while dest.exists():
                    dest = orig.with_name(f"{orig.stem}_restored_{counter}{orig.suffix}")
                    counter += 1
                shutil.move(str(curr), str(dest))
                created_dirs.add(curr.parent)
                restored += 1

        # Clean up empty category folders created during sort
        for folder in created_dirs:
            try:
                if folder.exists() and folder.is_dir() and not any(folder.iterdir()):
                    folder.rmdir()
            except OSError:
                pass

        target_session["undone"] = True
        self._write_json(self.history_path, history)
        return True, f"Restored {restored} file(s) from Session #{target_session['session_id']}.", restored
