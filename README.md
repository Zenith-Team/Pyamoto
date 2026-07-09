<img alt="banner" src="https://github.com/user-attachments/assets/ab7c7183-2f5c-4e8b-8f54-1283ba3ddfb3" />
<div align="center">
    <img alt="wiiu" height="56" src="https://github.com/user-attachments/assets/c22393cf-f619-4a1c-bc99-de68d5d903fa">
    <a href="https://go.nsmbu.net/discord">
        <img alt="discord" height="56" src="https://github.com/user-attachments/assets/f43b9deb-376a-48cd-bc09-8117cde071bb">
    </a>
    <a href="https://zenith.nsmbu.net/wiki/Miyamoto_Level_Editor">
        <img alt="docs" height="56" src="https://github.com/user-attachments/assets/f492ac70-08e4-4894-a4f8-a8a829d9e4e4">
    </a>
</div>

## Overview
Pyamoto is an advanced fork of the original Miyamoto editor with the purpose of improving functionality and usability.

## Installation
Download the latest release from the [releases page](https://github.com/Zenith-Team/Pyamoto/releases/latest).

## Usage
Follow the guide on the [wiki](https://zenith.nsmbu.net/wiki/Miyamoto_Level_Editor).

## Running from Source

**Prerequisites:** [Python 3](https://www.python.org/downloads/) (Windows: check "Add Python to PATH" during install), Git.

```bash
git clone https://github.com/Zenith-Team/Pyamoto
cd Pyamoto
bash setup_venv.sh
.venv/bin/python3 pyamoto.py   # macOS/Linux
# or on Windows:
# .venv\Scripts\python pyamoto.py
```

## Building from Source

Install the extra build dependencies, then run the release script:

```bash
.venv/bin/pip install "cx_Freeze==8.4.1"  # omit on Windows/Linux if not building
bash build_release.sh          # uses the version in project.json
bash build_release.sh 1.1      # override the version
```

- **macOS** — produces `Pyamoto-v<version>-macOS-x86_64.zip` in the repo root.
- **Windows / Linux** — produces `distrib/miyamoto_v<version>/` ready to zip.
