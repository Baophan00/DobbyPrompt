import os
import base64
import aiohttp
from typing import Optional, Dict, Any
import logging
from fireworks.client import Fireworks

logger = logging.getLogger(__name__)

class ImageProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fireworks_client = Fireworks(api_key=api_key)

    async def generate_image(self, prompt: str, model: str = None) -> Optional[Dict[str, Any]]:
        """Generate image using Fireworks AI image models"""
        try:
            model = model or os.getenv("FIREWORKS_IMAGE_MODEL", "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0")
            
            response = self.fireworks_client.images.generate(
                model=model,
                prompt=prompt,
                width=1024,
                height=1024,
                steps=20,
                n=1
            )
            
            if response and response.data:
                image_data = response.data[0]
                return {
                    "url": image_data.url,
                    "prompt": prompt,
                    "model": model,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
        return None

    async def generate_image_from_text(self, text_prompt: str) -> Optional[Dict[str, Any]]:
        """First generate image prompt from text, then create image"""
        try:
            # Generate detailed image prompt
            image_prompt_query = f"Create a detailed Stable Diffusion prompt for: {text_prompt}. Include style, composition, lighting, mood, and technical details."
            
            response = self.fireworks_client.chat.completions.create(
                model=os.getenv("FIREWORKS_MODEL"),
                messages=[{"role": "user", "content": image_prompt_query}],
                max_tokens=200
            )
            
            if response.choices:
                image_prompt = response.choices[0].message.content
                # Generate actual image
                return await self.generate_image(image_prompt)
                
        except Exception as e:
            logger.error(f"Image prompt generation error: {e}")
            
        return None