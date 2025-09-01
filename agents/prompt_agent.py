import logging
import os
from typing import AsyncIterator, Dict, Any
from dotenv import load_dotenv
from sentient_agent_framework import (
    AbstractAgent,
    Session,
    Query,
    ResponseHandler
)
from ..providers.model_provider import ModelProvider
from ..providers.prompt_provider import PromptProvider

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