from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from config import settings
from routes import ingest, rules, analyze, results

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify TwelveLabs connection
    from services.twelvelabs_service import TwelveLabsService
    svc = TwelveLabsService()
    connected = svc.verify_connection()
    app.state.tl_connected = connected
    print(f"TwelveLabs connection: {'OK' if connected else 'FAILED - using pending key'}")
    yield

app = FastAPI(
    title="Compliance Guardian",
    description="Automated video compliance screening powered by TwelveLabs",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api", tags=["ingest"])
app.include_router(rules.router, prefix="/api", tags=["rules"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(results.router, prefix="/api", tags=["results"])

@app.get("/api/health")
async def health():
    from models import HealthResponse
    return HealthResponse(twelvelabs_connected=getattr(app.state, "tl_connected", False))

# Serve frontend as static files from the same server (no separate frontend server needed)
# This MUST be the last mount to avoid catching /api routes
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
