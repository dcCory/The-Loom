# created by Cory Pagel
# Main entry point for FastAPI application for "The Loom" web app

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

#import API routers
from app.api import story_routes
from app.api import writer_block_routes
from app.api import project_routes
from app.api import character_routes
from app.api import plot_routes

#initializes FastAPI app
app = FastAPI(
    title="AI Writing Environment Backend",
    description="Backend API for local AI-assisted creative writing.",
    version="0.1.0"
)

# Cross-Origin Resource Sharing
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# API routers
app.include_router(story_routes.router, prefix="/api/story", tags=["Story Generation"])
app.include_router(writer_block_routes.router, prefix="/api/writer-block", tags=["Writer's Block Buster Tools"])
app.include_router(project_routes.router, prefix="/api/project", tags=["Project Management"])
app.include_router(character_routes.router, prefix="/api/character", tags=["Character Management"])
app.include_router(plot_routes.router, prefix="/api/plot", tags=["Plot-Point Management"])

# Root endpoint for basic testing
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Writing Environment Backend!"}



