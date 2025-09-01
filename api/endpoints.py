from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use absolute import
try:
    from agents.prompt_agent import PromptAgent
except ImportError:
    # Fallback
    from sentient_image_agent.agents.prompt_agent import PromptAgent

router = APIRouter()
agent = PromptAgent(name="Fireworks Chat Agent")

@router.post("/chat")
async def chat_endpoint(request: dict):
    """Simple chat endpoint (non-streaming)"""
    try:
        prompt = request.get("prompt", "")
        session_id = request.get("session_id", "default")
        
        # For demo purposes - in real implementation, use the agent properly
        return {"response": "Streaming endpoint available at /stream"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream")
async def stream_response(prompt: str, session_id: str = "default"):
    """SSE endpoint for streaming responses"""
    async def event_generator():
        try:
            # Initialize the agent
            agent = PromptAgent(name="Fireworks Chat Agent")
            
            # Create mock session and query
            session = Session(session_id=session_id)
            query = Query(prompt=prompt)
            
            # Create custom response handler for SSE
            class SSEResponseHandler:
                def __init__(self):
                    pass
                
                async def emit_text_block(self, type: str, text: str):
                    yield f"data: {json.dumps({'type': type, 'data': text})}\n\n"
                
                async def emit_json(self, type: str, data: dict):
                    yield f"data: {json.dumps({'type': type, 'data': data})}\n\n"
                
                async def emit_error(self, type: str, data: dict):
                    yield f"data: {json.dumps({'type': type, 'data': data})}\n\n"
                
                def create_text_stream(self, type: str):
                    return SSEStreamEmitter(type)
                
                async def complete(self):
                    yield f"data: {json.dumps({'type': 'DONE', 'data': {}})}\n\n"
            
            class SSEStreamEmitter:
                def __init__(self, type: str):
                    self.type = type
                
                async def emit_chunk(self, chunk: str):
                    yield f"data: {json.dumps({'type': 'AI_RESPONSE_CHUNK', 'data': chunk})}\n\n"
                
                async def complete(self):
                    pass
            
            # Process the query with real agent
            handler = SSEResponseHandler()
            await agent.assist(session, query, handler)
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'ERROR', 'data': {'message': str(e)}})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.get("/templates")
async def list_templates():
    """Get available prompt templates"""
    return {
        "templates": {
            "creative": "Creative writing template",
            "technical": "Technical explanation template",
            "simple": "Simple direct response",
            "detailed": "Detailed analysis template"
        }
    }