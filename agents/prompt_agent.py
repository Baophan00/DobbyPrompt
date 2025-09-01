import logging
import os
import sys
from typing import AsyncIterator, Dict, Any
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fallback implementation since sentient-agent-framework 0.1.1 doesn't have the expected classes
from abc import ABC, abstractmethod
from typing import Optional

class Session:
    def __init__(self, session_id: str = None):
        self.session_id = session_id

class Query:
    def __init__(self, prompt: str = ""):
        self.prompt = prompt

class ResponseHandler:
    def __init__(self):
        pass
    
    async def emit_text_block(self, type: str, text: str):
        print(f"[{type}] {text}")
    
    async def emit_json(self, type: str, data: dict):
        print(f"[{type}] {data}")
    
    async def emit_error(self, type: str, data: dict):
        print(f"[ERROR {type}] {data}")
    
    def create_text_stream(self, type: str):
        return StreamEventEmitter(type)
    
    async def complete(self):
        print("[COMPLETE]")

class StreamEventEmitter:
    def __init__(self, type: str):
        self.type = type
    
    async def emit_chunk(self, chunk: str):
        print(f"[{self.type} CHUNK] {chunk}")
    
    async def complete(self):
        print(f"[{self.type} COMPLETE]")

class AbstractAgent(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def assist(self, session: Session, query: Query, response_handler: ResponseHandler):
        pass

# Import providers using absolute path
from providers.model_provider import ModelProvider
from providers.prompt_provider import PromptProvider

load_dotenv()
logger = logging.getLogger(__name__)

class PromptAgent(AbstractAgent):
    def __init__(self, name: str = "Fireworks Prompt Agent"):
        super().__init__(name)
        
        # Initialize model provider with Fireworks
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY is not set")
        self._model_provider = ModelProvider(api_key=api_key)
        
        # Initialize prompt provider
        self._prompt_provider = PromptProvider()

    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """Process user query with prompt templates using Fireworks AI"""
        try:
            # Check if this is an image generation request
            if self._is_image_request(query.prompt):
                await self._handle_image_generation(query.prompt, response_handler)
                return

            # Extract template name if provided
            template_name = self._extract_template_name(query.prompt)
            
            # Get or create prompt template
            await response_handler.emit_text_block(
                "PROCESSING", "🚀 Preparing prompt template with Fireworks AI..."
            )
            
            if template_name:
                prompt_template = await self._prompt_provider.get_template(template_name)
                formatted_prompt = prompt_template.format(prompt=query.prompt)
                await response_handler.emit_json(
                    "TEMPLATE_INFO", 
                    {
                        "template_name": template_name,
                        "template_format": prompt_template
                    }
                )
            else:
                formatted_prompt = query.prompt

            # Show formatted prompt
            await response_handler.emit_json(
                "PROMPT_DETAILS", 
                {
                    "original_prompt": query.prompt,
                    "formatted_prompt": formatted_prompt,
                    "template_used": template_name or "none",
                    "model_provider": os.getenv("MODEL_PROVIDER", "fireworks")
                }
            )

            # Stream response from Fireworks AI
            response_stream = response_handler.create_text_stream("AI_RESPONSE")
            
            async for chunk in self._model_provider.query_stream(formatted_prompt):
                await response_stream.emit_chunk(chunk)
            
            await response_stream.complete()
            await response_handler.complete()

        except Exception as e:
            logger.error(f"Error in assist: {e}")
            await response_handler.emit_error(
                "ERROR", {"message": f"An error occurred: {str(e)}"}
            )
            await response_handler.complete()

    def _extract_template_name(self, prompt: str) -> str:
        """Extract template name from prompt if specified with @ prefix"""
        if prompt.startswith("@"):
            parts = prompt.split(" ", 1)
            return parts[0][1:].lower()  # Remove @ symbol and convert to lowercase
        return ""

    def _is_image_request(self, prompt: str) -> bool:
        """Check if the prompt is requesting image generation"""
        image_keywords = ['generate image', 'create image', 'make a picture', 'draw', 'photo', 'visualize', 'image of', 'picture of']
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in image_keywords)

    async def _handle_image_generation(self, prompt: str, response_handler: ResponseHandler):
        """Handle image generation requests"""
        try:
            await response_handler.emit_text_block(
                "PROCESSING", "🎨 Generating image prompt..."
            )
            
            # Generate image using the image provider
            image_result = await self._model_provider.image_provider.generate_image_from_text(prompt)
            
            if image_result and image_result.get("success"):
                await response_handler.emit_json(
                    "IMAGE_GENERATED", 
                    {
                        "image_url": image_result["url"],
                        "prompt": image_result["prompt"],
                        "type": "image"
                    }
                )
            else:
                error_msg = image_result.get("error", "Unknown error occurred") if image_result else "Failed to generate image"
                await response_handler.emit_error(
                    "IMAGE_ERROR", 
                    {"message": f"Image generation failed: {error_msg}"}
                )
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await response_handler.emit_error(
                "ERROR", 
                {"message": f"Image generation failed: {str(e)}"}
            )
        
        await response_handler.complete()