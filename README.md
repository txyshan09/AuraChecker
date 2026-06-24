# Aura Checker

A Vercel-ready FastAPI web app scaffold.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.index:app --reload
```

Open `http://127.0.0.1:8000`.

## Deploy To Vercel

1. Push this folder to a GitHub repository.
2. Import the repository at Vercel.
3. Use the default settings.
4. Vercel will detect `vercel.json` and deploy the FastAPI app.

## Project Shape

```text
api/index.py          FastAPI application entrypoint
static/styles.css     Front-end styling
templates/index.html  Main website view
requirements.txt      Python dependencies
vercel.json           Vercel routing config
```
