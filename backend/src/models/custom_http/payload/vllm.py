from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import json


@dataclass
class VllmPayload:
    model: str
    prompt: str
    stream: bool = False
    params: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def validate(self) -> Optional[str]:
        if not self.model:
            return "Model not found in data"
        return None

    def add_prompt(self, prompt: str):
        self.prompt = prompt
