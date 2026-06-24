import os
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field

# Locate base directory for robust path resolution on Vercel
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize FastAPI app (no root_path — Vercel passes full paths to the ASGI handler)
app = FastAPI(title="Aura Checker")

# 1. FIXED STATIC & TEMPLATE PATHS (using absolute paths resolved from BASE_DIR)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 2. CORS MIDDLEWARE FOR COOKIE TRANSMISSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://aura-checker-ten.vercel.app", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. SECURE ENVIRONMENT VARIABLES LOADED FROM VERCEL
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY", "aura-check-fallback-local-key-2026")

# 4. COOKIE STORAGE CONFIGURATION FOR VERCEL HANDSHAKE
IS_VERCEL = bool(os.getenv("VERCEL_URL"))
app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="aura_session",
    same_site="lax",
    https_only=IS_VERCEL
)

# 5. GOOGLE OAUTH INITIALIZATION
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# 6. PYDANTIC REQUEST MODEL FOR AURA CHECK
class AuraRequest(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    birth_month: int = Field(ge=1, le=12)
    mood: Literal["calm", "locked-in", "chaotic", "romantic", "mysterious"]
    focus: Literal["money", "love", "school", "fame", "peace"]
    binding_name: str = Field(default="", max_length=40)
    binding_platform: str = Field(default="", max_length=40)

AURAS = [
    ("Neon Sage", "#4de2ff", "sharp intuition, quiet confidence, and future-facing focus"),
    ("Solar Velvet", "#ffd166", "warm magnetism, lucky timing, and main-character pull"),
    ("Crimson Pulse", "#ff7d6e", "bold emotion, fearless moves, and impossible-to-ignore energy"),
    ("Violet Static", "#9b87ff", "mystery, creative voltage, and unpredictable charm"),
    ("Lime Halo", "#b9f75c", "fresh momentum, clean ambition, and comeback energy"),
]

# 7. ROUTE: HOME PAGE RENDER (supporting both / and /api/)
@app.get("/")
@app.get("/api/")
async def read_root(request: Request):
    user = request.session.get("user", None)
    try:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "user": user,
            "signal_score": "0000" if not user else "9999"
        })
    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "traceback": traceback.format_exc(),
            "template_dir": str(BASE_DIR / "templates"),
        })

# 8. ROUTE: GOOGLE AUTH LOGIN INITIALIZATION (supporting both paths)
@app.get("/auth/login")
@app.get("/api/auth/login")
async def login(request: Request):
    base = str(request.base_url).rstrip("/")
    redirect_uri = f"{base}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

# 9. ROUTE: OAUTH CALLBACK HANDSHAKE (supporting both paths)
@app.get("/auth/callback")
@app.get("/api/auth/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            first_name = user_info.get("given_name", "User")
            email = user_info.get("email", "")
            
            # Write session data securely
            request.session["user"] = first_name
            request.session["email"] = email
            
            return RedirectResponse(url="/")
            
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"OAuth Handshake Error: {str(e)}"})

# 10. ROUTE: LOGOUT (supporting both paths)
@app.get("/auth/logout")
@app.get("/api/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

# 11. ROUTE: HEALTH CHECK (supporting both paths)
@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "aura-checker"}

# 12. ROUTE: AURA CALCULATION (supporting both paths)
@app.post("/aura")
@app.post("/api/aura")
async def aura(payload: AuraRequest):
    allowed_platforms = {"google", "instagram", "tiktok", "x"}
    if payload.binding_platform not in allowed_platforms:
        payload.binding_platform = ""

    seed_text = f"{payload.name}|{payload.birth_month}|{payload.mood}|{payload.focus}|{payload.binding_platform}|{payload.binding_name}"
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

        if payload.binding_platform:
            binding_label = f"{payload.binding_platform.title()} binding"

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
        "binding_platform": payload.binding_platform,
        "binding_score": binding_score,
        "binding_label": binding_label,
    }