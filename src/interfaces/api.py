"""REST API Interface - Web entry point.

This module provides the FastAPI application for interacting with the
decision system via REST endpoints.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
import os
import sys
import uvicorn
import asyncio
import json

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.domain.situations import Situation
from src.knowledge.knowledge_base import KnowledgeBase
from src.engine.decision_engine import DecisionEngine
from src.engine.models import DecisionResult
from src.analyzer.historical_analyzer import HistoricalAnalyzer
from src.analyzer.whatif_analyzer import WhatIfAnalyzer
from src.domain.situations import HistoricalSituation
from src.analyzer.models import AnalysisReport

# Global components
kb: KnowledgeBase = None
engine: DecisionEngine = None
historical_analyzer: HistoricalAnalyzer = None
whatif_analyzer: WhatIfAnalyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize system components on startup."""
    global kb, engine, historical_analyzer, whatif_analyzer
    
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
    
    # Initialize Engine
    engine = DecisionEngine(knowledge_base=kb)
    
    # Initialize Analyzers
    historical_analyzer = HistoricalAnalyzer(decision_engine=engine)
    whatif_analyzer = WhatIfAnalyzer(default_engine=engine)
    
    yield
    # Cleanup

app = FastAPI(
    title="Principles-Based Decision System API",
    description="API for analyzing situations against personal principles.",
    lifespan=lifespan
)

# Add CORS middleware for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        import uuid
        situation = Situation(
            id=str(uuid.uuid4()),
            description=request.description
        )
        
        result = engine.evaluate(situation)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/whatif", response_model=DecisionResult)
async def analyze_whatif(request: AnalysisRequest):
    """Analyze a situation using optional custom principles (currently just defaults)."""
    if not whatif_analyzer:
         raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        import uuid
        situation = Situation(
            id=str(uuid.uuid4()),
            description=request.description
        )
        
        # Future: accept custom principles in request body
        result = whatif_analyzer.analyze(situation)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HistoricalAnalysisRequest(BaseModel):
    description: str
    actual_decision: str
    actual_outcome: str

@app.post("/analyze/historical", response_model=AnalysisReport)
async def analyze_historical(request: HistoricalAnalysisRequest):
    """Analyze a past decision against principles."""
    if not historical_analyzer:
         raise HTTPException(status_code=503, detail="System not initialized")
         
    try:
        import uuid
        situation = HistoricalSituation(
            id=str(uuid.uuid4()),
            description=request.description,
            actual_decision=request.actual_decision,
            actual_outcome=request.actual_outcome
        )
        
        report = historical_analyzer.analyze(situation)
        return report
        
    except Exception as e:
        # print error for debugging
        print(f"Error in /analyze/historical: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/principles")
async def list_principles():
    """List all available principles."""
    if not kb:
        raise HTTPException(status_code=503, detail="System not initialized")
    return kb.principles

@app.get("/sops")
async def list_sops():
    """List all available SOPs."""
    if not kb:
        raise HTTPException(status_code=503, detail="System not initialized")
    return kb.sops

@app.get("/sops/{sop_id}")
async def get_sop(sop_id: int):
    """Get a specific SOP by ID."""
    if not kb:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    sop = kb.get_sop(sop_id)
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")
    return sop

# Mount Static Files
static_path = Path("src/interfaces/static")
if not static_path.exists():
    static_path = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")

def start():
    """Start the API server."""
    port = int(os.environ.get("PORT", 2947))
    uvicorn.run("src.interfaces.api:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    start()
