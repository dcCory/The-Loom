# created by Cory Pagel
# Main entry point for FastAPI application for "The Loom" web app

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

#import API routers
from app.api import story_routes
from app.api import character_routes

#initialize FastAPI app
app = FastAPI(
    title="AI Writing Environment Backend",
    description="Backend API for local AI-assisted creative writing.",
    version="0.1.0"
)

#Configures Cross-Origin Resource Sharing
#Tells the API what sources to expect calls from.
origins = [
    "http://localhost:3000", #default react development server port
    "http://127.0.0.1:3000"
    #Any other frontend origins can be added as necessary.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# API routers
app.include_router(story_routes.router, prefix="/api/story", tags=["Story Generation"])
app.include_router(character_routes.router, prefix="/api/character", tags=["Character Management"])

#Root endpoint for testing
@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Writing Environment Backend!"}



