from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process_query(self, prompt: str, session_id: str = None) -> AsyncIterator[Dict[str, Any]]:
        pass

    @abstractmethod
    async def initialize(self):
        pass