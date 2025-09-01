import os
from typing import AsyncIterator
import aiohttp
import json
import logging
from fireworks.client import Fireworks

logger = logging.getLogger(__name__)

class ModelProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider = os.getenv("MODEL_PROVIDER", "fireworks")
        
        if self.provider == "fireworks":
            self.fireworks_client = Fireworks(api_key=api_key)
        elif self.provider == "openai":
            import openai
            openai.api_key = api_key
        elif self.provider == "anthropic":
            import anthropic
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    async def query_stream(self, prompt: str) -> AsyncIterator[str]:
        if self.provider == "fireworks":
            async for chunk in self._fireworks_stream(prompt):
                yield chunk
        elif self.provider == "openai":
            async for chunk in self._openai_stream(prompt):
                yield chunk
        elif self.provider == "anthropic":
            async for chunk in self._anthropic_stream(prompt):
                yield chunk

    async def _fireworks_stream(self, prompt: str) -> AsyncIterator[str]:
        try:
            # Cập nhật API call cho phiên bản mới
            response = self.fireworks_client.chat.completions.create(
                model=os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/mixtral-8x7b-instruct"),
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=1000
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Fireworks API error: {e}")
            yield f"Error: {str(e)}"

    async def _openai_stream(self, prompt: str) -> AsyncIterator[str]:
        try:
            import openai
            response = await openai.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=1000
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            yield f"Error: {str(e)}"

    async def _anthropic_stream(self, prompt: str) -> AsyncIterator[str]:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            with client.messages.stream(
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            yield f"Error: {str(e)}"