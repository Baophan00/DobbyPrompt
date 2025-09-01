from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
from typing import AsyncGenerator
from agents.prompt_agent import PromptAgent  # Đã sửa import

router = APIRouter()
agent = PromptAgent(name="Fireworks Chat Agent")

@router.post("/chat")
async def chat_endpoint(request: dict):
    """Simple chat endpoint (non-streaming)"""
    try:
        prompt = request.get("prompt", "")
        # For demo purposes - in real implementation, use the agent properly
        return {"response": "Streaming endpoint available at /stream"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream")
async def stream_response(prompt: str, session_id: str = "default"):
    """SSE endpoint for streaming responses"""
    async def event_generator():
        try:
            # Simulate processing
            yield f"data: {json.dumps({'type': 'PROCESSING', 'data': 'Starting Fireworks AI...'})}\n\n"
            
            # Simulate template detection
            if prompt.startswith("@"):
                yield f"data: {json.dumps({'type': 'TEMPLATE_INFO', 'data': {'template_name': 'creative'}})}\n\n"
            
            # Simulate AI response chunks
            responses = [
                "I'm thinking about your question...",
                "This is an interesting topic!",
                "Let me provide you with a detailed response.",
                "Based on my analysis, here's what I think...",
                "In conclusion, this is a fascinating subject worth exploring further."
            ]
            
            for response in responses:
                yield f"data: {json.dumps({'type': 'AI_RESPONSE_CHUNK', 'data': response})}\n\n"
            
            # Completion
            yield f"data: {json.dumps({'type': 'DONE', 'data': {}})}\n\n"
            
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