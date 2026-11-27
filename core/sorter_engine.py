from pathlib import Path
import shutil


class SorterEngine:
    def __init__(self, history_manager):
        self.history_manager = history_manager
        self.rules = self.history_manager.load_rules()

    def reload_rules(self):
        self.rules = self.history_manager.load_rules()

    def scan_directory(self, folder_path: str) -> list[Path]:
        target = Path(folder_path)
        if not target.exists() or not target.is_dir():
            raise ValueError("Selected folder does not exist or is not a valid directory.")

        files = []
        for item in target.iterdir():
            if item.is_file() and not item.name.startswith("."):
                files.append(item)
        return sorted(files, key=lambda p: p.name.lower())

    def classify_file(self, file_path: Path) -> str:
        self.reload_rules()
        name_lower = file_path.name.lower()
        ext_lower = file_path.suffix.lower()

        # 1. Prioritize custom keyword rules
        for category, rule_data in self.rules.items():
            for kw in rule_data.get("keywords", []):
                if kw and kw.lower() in name_lower:
                    return category

        # 2. Match by file extension
        for category, rule_data in self.rules.items():
            exts = [e.lower() for e in rule_data.get("extensions", [])]
            if ext_lower in exts:
                return category

        return "Others"

    def resolve_conflict(self, dest_path: Path) -> Path:
        counter = 1
        candidate = dest_path
        while candidate.exists():
            candidate = dest_path.with_name(f"{dest_path.stem} ({counter}){dest_path.suffix}")
            counter += 1
        return candidate

    def generate_plan(self, folder_path: str) -> list[dict]:
        target = Path(folder_path)
        files = self.scan_directory(folder_path)
        plan = []
        planned_targets = set()

        for src in files:
            category = self.classify_file(src)
            dest_dir = target / category
            raw_dest = dest_dir / src.name
            final_dest = self.resolve_conflict(raw_dest)

            counter = 1
            while str(final_dest).lower() in planned_targets:
                final_dest = dest_dir / f"{src.stem} ({counter}){src.suffix}"
                counter += 1

            planned_targets.add(str(final_dest).lower())
            has_conflict = final_dest.name != src.name
            plan.append({
                "source_path": str(src),
                "filename": src.name,
                "original_rel": f"{target.name}/",
                "category": category,
                "destination_path": str(final_dest),
                "status": f"Conflict: Rename ({final_dest.stem.split('(')[-1].rstrip(')')})" if has_conflict else "Ready",
                "selected": True
            })
        return plan

    def execute_plan(self, folder_path: str, approved_moves: list[dict], progress_callback=None, source: str = "Manual Sort") -> dict:
        if not approved_moves:
            return {"moved_count": 0, "session": None}

        logged_moves = []
        total = len(approved_moves)

        for idx, item in enumerate(approved_moves, start=1):
            src = Path(item["source_path"])
            if not src.exists() or not src.is_file():
                continue

            dest = Path(item["destination_path"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            safe_dest = self.resolve_conflict(dest)

            shutil.move(str(src), str(safe_dest))
            logged_moves.append({
                "original_path": str(src),
                "new_path": str(safe_dest),
                "category": item["category"]
            })

            if progress_callback:
                progress_callback(idx, total, src.name)

        session = None
        if logged_moves:
            session = self.history_manager.log_session(folder_path, logged_moves, source=source)

        return {"moved_count": len(logged_moves), "session": session}
