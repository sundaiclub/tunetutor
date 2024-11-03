# Tune Tutotor

Generate educational jungles using Suno.

Hacked on [Sundai](https://sundai.club), Nov 3, 2024.

# Installation

```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Running 

## Locally

```bash
python main.py
```

## On Render
```bash
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4
```