"""REST API Interface - Web entry point.

This module provides the FastAPI application for interacting with the
decision system via REST endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
import os
import sys
import uvicorn

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.domain.situations import Situation
from src.knowledge.knowledge_base import KnowledgeBase
from src.engine.decision_engine import DecisionEngine
from src.engine.models import DecisionResult

# Global components
kb: KnowledgeBase = None
engine: DecisionEngine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize system components on startup."""
    global kb, engine
    
    # Initialize KB
    # Assuming run from root
    data_path = Path("data")
    if not data_path.exists():
        # Fallback
        data_path = Path(__file__).parent.parent.parent / "data"
    
    if not data_path.exists():
        print("Error: Could not find data directory.")
        
    kb = KnowledgeBase(data_path=data_path)
    kb.load()
    
    # Initialize Engine with Semantic Matching enabled
    engine = DecisionEngine(knowledge_base=kb)
    
    yield
    # Cleanup if needed

app = FastAPI(
    title="Principles-Based Decision System API",
    description="API for analyzing situations against personal principles.",
    lifespan=lifespan
)

# Mount Static Files
static_path = Path("src/interfaces/static")
# If running from different CWD, adjust logic
if not static_path.exists():
    static_path = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")

@app.get("/")
async def root():
    """Redirect to dashboard."""
    return RedirectResponse(url="/static/index.html")

class AnalysisRequest(BaseModel):
    description: str

class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/analyze", response_model=DecisionResult)
async def analyze_situation(request: AnalysisRequest):
    """Analyze a situation and get recommendations."""
    if not engine:
        raise HTTPException(status_code=503, detail="System not initialized")
        
    try:
        # Create situation object
        import uuid
        situation = Situation(
            id=str(uuid.uuid4()),
            description=request.description
        )
        
        # Evaluate
        result = engine.evaluate(situation)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/principles")
async def list_principles():
    """List all available principles."""
    if not kb:
        raise HTTPException(status_code=503, detail="System not initialized")
    return kb.principles

def start():
    """Start the API server."""
    # Custom port 2947 as requested
    uvicorn.run("src.interfaces.api:app", host="127.0.0.1", port=2947, reload=True)

if __name__ == "__main__":
    start()
