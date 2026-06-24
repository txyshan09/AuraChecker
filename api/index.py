from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Aura Checker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


class AuraRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    birth_month: int = Field(ge=1, le=12)
    mood: Literal["calm", "locked-in", "chaotic", "romantic", "mysterious"]
    focus: Literal["money", "love", "school", "fame", "peace"]
    binding_name: str = Field(default="", max_length=40)


AURAS = [
    ("Neon Sage", "#4de2ff", "sharp intuition, quiet confidence, and future-facing focus"),
    ("Solar Velvet", "#ffd166", "warm magnetism, lucky timing, and main-character pull"),
    ("Crimson Pulse", "#ff7d6e", "bold emotion, fearless moves, and impossible-to-ignore energy"),
    ("Violet Static", "#9b87ff", "mystery, creative voltage, and unpredictable charm"),
    ("Lime Halo", "#b9f75c", "fresh momentum, clean ambition, and comeback energy"),
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "signal_score": 88,
            "scan_state": "Aura",
        },
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "aura-checker"}


@app.post("/api/aura")
async def aura(payload: AuraRequest):
    seed_text = f"{payload.name}|{payload.birth_month}|{payload.mood}|{payload.focus}|{payload.binding_name}"
    seed = sum((index + 1) * ord(char) for index, char in enumerate(seed_text))
    aura_name, aura_color, aura_meaning = AURAS[seed % len(AURAS)]
    score = 62 + seed % 38
    binding_score = None
    binding_label = "Solo aura"

    if payload.binding_name.strip():
        binding_score = 51 + (seed // 7) % 49
        if binding_score >= 86:
            binding_label = "Rare aura bind"
        elif binding_score >= 72:
            binding_label = "Strong pull"
        elif binding_score >= 60:
            binding_label = "Unstable spark"
        else:
            binding_label = "Different frequencies"

    focus_lines = {
        "money": "Your money aura says move with proof, not panic. Build something small, useful, and repeatable.",
        "love": "Your love aura is selective. You attract better when you stop auditioning for attention.",
        "school": "Your study aura is strongest in short sprints. Win the next hour, then stack the hours.",
        "fame": "Your visibility aura is heating up. Post the thing that feels too specific to ignore.",
        "peace": "Your peace aura wants fewer tabs open in your brain. Protect your energy before spending it.",
    }

    return {
        "name": payload.name.strip(),
        "aura": aura_name,
        "color": aura_color,
        "score": score,
        "meaning": aura_meaning,
        "focus_reading": focus_lines[payload.focus],
        "binding_name": payload.binding_name.strip(),
        "binding_score": binding_score,
        "binding_label": binding_label,
    }
