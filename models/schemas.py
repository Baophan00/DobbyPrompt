from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"
    template_name: Optional[str] = None

class ChatResponse(BaseModel):
    type: str
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    message: str

class TemplateInfo(BaseModel):
    name: str
    description: str
    format: str