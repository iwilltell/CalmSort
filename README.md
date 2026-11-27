# 🗂️ CalmSort

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-1E3A5F?style=for-the-badge)](https://customtkinter.tomschimansky.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)]()

**CalmSort** is a modern, cross-platform desktop file management and automated sorting system built with Python and CustomTkinter. Designed to eliminate cluttered `Downloads` and `Desktop` directories without risking accidental data loss, it pairs a responsive dark/light GUI with a decoupled 3-layer architecture featuring dry-run previews, SHA-256 deduplication, real-time folder monitoring, and one-click session rollbacks.

---

## ✨ Key Features

* **🧠 Priority Rule-Based Classification:** Automatically categorizes files into structured folders (`Documents`, `Images`, `Videos`, `Audio`, `Code`, `Archives`, `Installers`, and custom categories). Custom filename **keyword rules** always take priority over extension mappings.
* **🔍 Safe Dry-Run Preview Mode:** Inspect a complete `Source → Destination` table with category badges, conflict warnings, and individual inclusion checkboxes *before* a single file is moved on disk.
* **🛡️ Non-Destructive Collision Resolution:** Never overwrites existing files. If `Report.pdf` already exists in the destination folder, CalmSort automatically renames incoming duplicates to `Report (1).pdf`.
* **♻️ Chunked SHA-256 Duplicate Finder:** Filters candidates by byte size first and computes 64 KB chunked SHA-256 cryptographic hashes to detect exact duplicate files regardless of filename, displaying recoverable storage space.
* **👁️ Real-Time "Live Watch" Mode:** Powered by `watchdog`, automatically detects and sorts newly downloaded files in the background as soon as they finish writing to disk.
* **↩️ Persistent Activity Log & 1-Click Undo:** Every sorting batch is logged with a unique session ID in `data/history.json`, enabling instant, complete rollback of any session back to original file paths.
* **🎨 Modern UI/UX:** Built with `CustomTkinter`, featuring sidebar navigation, live progress bars, multithreaded background workers (zero UI freezing), and a Dark/Light theme switcher.

---

## 🏗️ System Architecture

CalmSort follows a clean **3-Layer Modular Architecture** that decouples interface rendering from file-system operations and persistent JSON storage:

```text
+-------------------------------------------------------------------+
|                  main.py (Application Entry Point)                |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                PRESENTATION LAYER (CustomTkinter GUI)             |
|   ui/app_window.py (Sidebar, Theme Switch, Folder Picker)         |
|   ui/preview_frame.py (Dry-Run Preview Table & Checkboxes)        |
+---------------------------------+---------------------------------+
         | User Actions / Callbacks        ^ Progress / Updates
         v                                 |
+-------------------------------------------------------------------+
|                     LOGIC LAYER (Core Engine)                     |
|   core/sorter_engine.py     |  core/duplicate_finder.py           |
|   core/watcher.py (Watchdog Real-Time Directory Monitor)          |
+---------------------------------+---------------------------------+
                                  | Read / Write Rules & Logs
                                  v
+-------------------------------------------------------------------+
|                  STORAGE LAYER (Local JSON Files)                 |
|   storage/history_manager.py  --->  data/rules.json & history.json|
+-------------------------------------------------------------------+
```

---

## 📂 Project Structure

```text
CalmSort/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── core/
│   ├── sorter_engine.py         # Keyword/extension classification, dry-run planner, conflict resolver
│   ├── duplicate_finder.py      # Size grouping & 64 KB chunked SHA-256 duplicate scanner
│   └── watcher.py               # Background watchdog listener for Live Watch mode
├── storage/
│   └── history_manager.py       # JSON persistence for rules.json, history.json, and session Undo
├── ui/
│   ├── app_window.py            # Main CustomTkinter window, sidebar navigation, & view frames
│   └── preview_frame.py         # Interactive Dry-Run Preview table with selection checkboxes
└── data/                        # Auto-generated on first launch
    ├── rules.json               # Default & custom category mappings
    └── history.json             # Timestamped transaction logs for Undo rollbacks
```

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.11** or higher
* `pip` package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iwilltell/CalmSort.git
   cd CalmSort
   ```

2. **Create and activate a virtual environment (Recommended):**
   * **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch CalmSort:**
   ```bash
   python main.py
   ```

---

## 📖 Usage Guide

1. **Organize & Dry-Run Preview:**
   * Click **Select Target Folder** to choose a cluttered directory (defaults to `Downloads`).
   * Click **Scan & Preview** to inspect proposed destination categories and rename alerts.
   * Uncheck any files you want to leave untouched, then click **Confirm Checked Moves**.
2. **Live Watch Automation:**
   * Toggle **Live Watch** ON in the Organize top bar to automatically sort incoming files in real time.
3. **Custom Rules Manager:**
   * Navigate to the **Rules** tab to add custom categories (e.g., Category: `Finance`, Extensions: `.pdf, .xlsx`, Keywords: `invoice, receipt`).
4. **Duplicate Cleaner:**
   * Navigate to the **Duplicates** tab and click **Scan for Duplicates**. Original copies remain unchecked by default for safety; click **Delete Checked Duplicates** to reclaim disk space.
5. **History & One-Click Undo:**
   * Navigate to the **History** tab to audit past sorting sessions and click **Undo This Session** (or **Undo Latest Session**) to restore files to their original paths and remove empty category folders.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Core logic, concurrency, and cross-platform file I/O |
| **GUI Framework** | `CustomTkinter` | Modern dark/light desktop widgets, tables, and progress bars |
| **File System** | `pathlib` & `shutil` | Cross-platform path resolution and safe file transfers |
| **Deduplication** | `hashlib` (SHA-256) | Cryptographic content verification for duplicate files |
| **Folder Monitor** | `watchdog` | Event-driven real-time directory observation |
| **Persistence** | `json` | Human-readable rule storage and reversible transaction logs |

---

## 👤 Author

**Wibhor Kumar Roy**  
* Course: Python Project (CSM 216) — Lovely Professional University  
* GitHub: [@iwilltell](https://github.com/iwilltell)