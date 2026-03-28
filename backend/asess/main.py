from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asess.routes import user_routes
from asess.routes import ai
from asess.core.database import engine, Base
from asess.models.patient import Patient  # noqa: F401 - ensure table is created

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ASESS - Eye Screening System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow cross-origin requests from the frontend service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routes only ---
app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "backend"}