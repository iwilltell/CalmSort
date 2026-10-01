# CalmSort 🌫️

> A calm, safe, intelligent file organization system.

CalmSort is a desktop-first file organization system designed to reduce digital clutter without taking control away from the user.

The project combines a **Python desktop application** with a separate **Android companion app**. The desktop application will detect files, understand their context, classify them using weighted signals, organize only when confidence is high, and keep a transparent history of what happened.

## ✨ Design Philosophy

CalmSort is built around one idea:

> **The computer should quietly manage the clutter so the user can focus on their work.**

### UX principles

- 🌫️ Calm, minimal, glassmorphism-inspired interface
- 🧠 Explainable automation instead of a black box
- 🛡️ Safety before automation
- 👀 Preview and review when confidence is low
- ↩️ Recoverable file operations
- 📱 PC as the control center, Android as the companion
- 🎯 Simple by default, detailed when needed

## 🖥️ Platform Roles

### PC — Control Center

The desktop application handles the main workload:

- Folder scanning
- File classification
- Confidence scoring
- Safe organization
- Duplicate detection
- Operation history
- Real-time monitoring
- Rules and settings

### Android — Companion

The Android application is intentionally simpler and focuses on:

- Current CalmSort status
- Recent activity
- Files waiting for review
- Notifications
- Basic statistics
- Selected remote controls in a later phase

Both clients communicate with the same CalmSort backend rather than duplicating the organization logic.

## 🧩 Architecture

```text
                         ┌─────────────────────┐
                         │   CalmSort Engine   │
                         │                     │
                         │ Scanner             │
                         │ Classifier          │
                         │ Confidence          │
                         │ Organizer           │
                         │ SQLite              │
                         │ Duplicate Detection│
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
             ┌──────▼──────┐                 ┌──────▼──────┐
             │     PC      │                 │   Android   │
             │  PySide6   │                 │  Companion  │
             └─────────────┘                 └─────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                              FastAPI / JSON
```

## 📁 Project Structure

```text
CalmSort/
├── app/
│   ├── core/          # Configuration, logging, shared domain logic
│   ├── services/      # Scanner, classifier, organizer, database, monitor, API
│   ├── ui/            # PySide6 desktop interface
│   ├── __init__.py
│   └── main.py
│
├── tests/             # Automated tests
├── data/              # Local runtime data; ignored by Git
├── .github/           # GitHub workflows and project configuration
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| PySide6 | Desktop GUI |
| pathlib / shutil | Safe file-system operations |
| hashlib | SHA-256 duplicate detection |
| SQLite | Local history and application data |
| watchdog | Real-time folder monitoring |
| FastAPI | PC ↔ Android API |
| HTTP / JSON | Client communication |

## 🔐 Safety Model

CalmSort should never blindly move files.

The planned organization flow is:

```text
Detect file
    ↓
Extract signals
    ↓
Classify
    ↓
Calculate confidence
    ↓
 ┌───────────────┐
 │ High confidence│ ──→ Safe automatic organization
 └───────────────┘

 ┌───────────────┐
 │ Low confidence │ ──→ User review
 └───────────────┘
```

The confidence threshold will be configurable. The initial target is **70%**, but this will not be treated as a permanent hard-coded value.

Planned safety features include:

- Preview / dry-run mode
- No silent overwrites
- Collision handling
- Protected folders
- Exclusion rules
- Operation history
- Undo support
- Error logging

## 🚧 Development Status

### Module 1 — Foundation

**Status: Complete**

- [x] Project structure
- [x] Python package foundation
- [x] PySide6 desktop shell
- [x] Central configuration
- [x] Logging foundation
- [x] Basic tests
- [x] Initial visual direction

### Module 2 — File Detection Engine

**Status: Next**

Planned:

- [ ] Folder selection
- [ ] Safe recursive scanning
- [ ] File metadata model
- [ ] File type detection
- [ ] Scan results
- [ ] Unit tests

### Future Modules

- Classification engine
- Confidence scoring
- Safe organizer
- SQLite history
- Duplicate detection
- Real-time monitoring
- Desktop UI expansion
- FastAPI backend
- Android companion
- Integration and polish

## 💻 Development Setup

Python **3.11+** is recommended.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Run CalmSort

```powershell
python -m app.main
```

### Run Tests

```powershell
pytest
```

## 🔄 Development Workflow

CalmSort is developed one module at a time.

```text
Build module
    ↓
Write tests
    ↓
Run tests
    ↓
Review / polish
    ↓
Commit
    ↓
Push to GitHub
    ↓
Start next module
```

Every milestone should leave the project in a working state.

## 📌 Project Goal

Turn a messy file folder into a **calmer, safer, searchable workspace** while keeping the user informed and in control.

---

**CalmSort** — Intelligent Automatic File Organization System
