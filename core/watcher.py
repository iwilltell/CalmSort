from pathlib import Path
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class _SortEventHandler(FileSystemEventHandler):
    def __init__(self, folder_path: str, engine, on_sorted_callback=None):
        super().__init__()
        self.folder_path = Path(folder_path)
        self.engine = engine
        self.on_sorted_callback = on_sorted_callback

    def on_created(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        if src.parent != self.folder_path or src.name.startswith("."):
            return
        if src.suffix.lower() in {".tmp", ".crdownload", ".part"}:
            return

        # Small delay so browser/OS finishes writing the file handle
        time.sleep(0.6)
        if not src.exists():
            return

        category = self.engine.classify_file(src)
        dest_dir = self.folder_path / category
        dest = self.engine.resolve_conflict(dest_dir / src.name)
        move_item = [{
            "source_path": str(src),
            "destination_path": str(dest),
            "category": category
        }]
        result = self.engine.execute_plan(str(self.folder_path), move_item, source="Live Watch")
        if result["moved_count"] > 0 and self.on_sorted_callback:
            self.on_sorted_callback(src.name, category)


class FolderWatcher:
    def __init__(self, engine, on_sorted_callback=None):
        self.engine = engine
        self.on_sorted_callback = on_sorted_callback
        self.observer = None
        self.watched_path = None

    @property
    def is_running(self) -> bool:
        return self.observer is not None and self.observer.is_alive()

    def start(self, folder_path: str):
        self.stop()
        target = Path(folder_path)
        if not target.exists() or not target.is_dir():
            raise ValueError("Cannot start Live Watch on an invalid directory.")

        handler = _SortEventHandler(str(target), self.engine, self.on_sorted_callback)
        self.observer = Observer()
        self.observer.schedule(handler, str(target), recursive=False)
        self.observer.start()
        self.watched_path = str(target)

    def stop(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=2)
            self.observer = None
            self.watched_path = None
