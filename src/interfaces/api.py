"""REST API Interface - Web entry point.

This module provides the FastAPI application for interacting with the
decision system via REST endpoints.
"""

from fastapi import FastAPI, HTTPException, Request
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
    
    # Initialize Engine
    engine = DecisionEngine(knowledge_base=kb)
    
    yield
    # Cleanup

app = FastAPI(
    title="Principles-Based Decision System API",
    description="API for analyzing situations against personal principles.",
    lifespan=lifespan
)

# ... Static mount ...

async def analysis_generator(description: str):
    """Generates SSE events for the analysis process."""
    yield f"data: {json.dumps({'status': 'matching_started', 'message': 'Starting analysis...'})}\n\n"
    await asyncio.sleep(0.5) # Simulate work
    
    # 1. Semantic
    yield f"data: {json.dumps({'status': 'semantic_processing', 'message': 'Generating embeddings...'})}\n\n"
    # Actually run the match?
    # For streaming, we might need to break down the engine.evaluate method or just call it and report 'done'.
    # Since evaluate is synchronous, it blocks.
    # To truly stream, we'd need to make engine async or run in thread.
    
    # Run analysis in threadpool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: engine.evaluate(Situation(description=description)))
    
    yield f"data: {json.dumps({'status': 'semantic_done', 'message': 'Semantic matching complete'})}\n\n"
    await asyncio.sleep(0.3)
    
    yield f"data: {json.dumps({'status': 'keyword_done', 'message': 'Keyword matching complete'})}\n\n"
    
    # Send final result
    # We need to serialize the result. Models are dataclasses, Pydantic can handle if we convert.
    # Or just dict.
    
    # Quick serialization helper
    def serialize(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    # Serialize complex object
    # We'll use pydantic's jsonable_encoder if available, or simple dict dump for now
    # Since DecisionResult is a dataclass, asdict works
    from dataclasses import asdict
    res_dict = asdict(result)
    # Fix nested dataclasses and enums if any (PrincipleMatch, etc) is recursive
    # asdict handles recursion for dataclasses.
    # But explicit conversion for safe JSON:
    
    # Convert 'applicable_principles' list of PrincipleMatch
    # Convert 'triggered_sops' list of SOP
    
    # Just sending the whole result as 'complete'
    # Use a custom encoder for json dumps
    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if hasattr(o, '__dict__'):
                return o.__dict__
            return super().default(o)
            
    final_json = json.dumps({'status': 'complete', 'result': res_dict}, cls=EnhancedJSONEncoder)
    yield f"data: {final_json}\n\n"

@app.get("/analyze/stream")
async def analyze_stream(description: str):
    """Stream analysis progress using SSE."""
    return StreamingResponse(analysis_generator(description), media_type="text/event-stream")

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
