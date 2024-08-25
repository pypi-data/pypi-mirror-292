from litellm import completion
from .BaseAgent import BaseAgent
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class ReActAgent(BaseAgent):
    def send_completion_request(self, plan: str, depth: int = 0) -> Dict:
        raise NotImplementedError("This method should be implemented by subclasses")