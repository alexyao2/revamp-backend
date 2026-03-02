from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import reels, notes, habits
from app.routes import auth
from app.db.database import engine, Base

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Revamp API",
    description="Backend for Revamp - Instagram Reel to Notes App",
    version="0.1.0"
)

# CORS - update origins when you have a real domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(reels.router, prefix="/api/reels", tags=["Reels"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(habits.router, prefix="/api/habits", tags=["Habits"])

@app.get("/")
def health_check():
    return {"status": "ok", "app": "Revamp API", "version": "0.1.0"}
