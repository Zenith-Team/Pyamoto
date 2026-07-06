# Pyamoto
## The New Super Mario Bros. U level editor
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
