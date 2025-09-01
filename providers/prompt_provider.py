import json
import os
from typing import Dict, Any

class PromptProvider:
    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        # Default templates
        return {
            "creative": "You are a creative writer. Expand on this idea: {prompt}",
            "technical": "As a technical expert, explain: {prompt}",
            "simple": "{prompt}",
            "detailed": "Provide a detailed analysis of: {prompt}",
            "image": "Create a detailed prompt for generating an image of: {prompt}. Include style, composition, lighting, and mood details.",
            "photo": "Generate a photorealistic image description of: {prompt}. Include camera settings, lighting, and environment details."
        }

    async def get_template(self, template_name: str) -> str:
        return self.templates.get(template_name, "{prompt}")

    async def add_template(self, name: str, template: str):
        self.templates[name] = template

    async def list_templates(self) -> Dict[str, str]:
        return self.templates
