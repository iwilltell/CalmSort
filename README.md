# CalmSort

An Automated Desktop File Management and Sorting System built with Python and CustomTkinter.

## Features
- **Smart Rule-Based Sorting**: Categorizes files using custom filename keywords and file extensions.
- **Dry-Run Preview Mode**: Inspect and selectively approve proposed file moves before modifying disk files.
- **SHA-256 Duplicate Finder**: Detects exact duplicate files via chunked cryptographic hashing.
- **Live Watch Mode**: Real-time folder monitoring using `watchdog`.
- **One-Click Undo**: Reverts completed sorting sessions using persistent JSON transaction logs.

## Setup & Run
```bash
pip install -r requirements.txt
python main.py
```
