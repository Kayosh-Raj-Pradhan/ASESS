from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from asess.routes import user_routes
from asess.routes import ai
from asess.core.database import engine, Base
from asess.models.user import User
from asess.models.scan import ScanResult

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASESS - Eye Screening System")

# Allow cross-origin requests from the frontend (during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

@app.get("/", tags=["root"])
def read_root():
    return RedirectResponse(url="/static/index.html")

app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])