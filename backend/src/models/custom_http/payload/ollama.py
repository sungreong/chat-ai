from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import json


class OllamaPayload:
    def __init__(self, prompt: str, **kwargs):
        self.prompt = prompt
        self.options = {}

        # Filter and add remaining keyword arguments to the options dictionary
        recognized_keys = {"model", "prompt", "stream"}
        for key, value in kwargs.items():
            if key not in recognized_keys:
                self.options[key] = value
            else:
                setattr(self, key, value)
        for key in recognized_keys:
            if hasattr(self, key):
                continue
            else:
                if key == "stream":
                    setattr(self, key, False)
                else:
                    raise ValueError(f"Missing required argument: {key}")

    def to_json(self) -> str:
        payload_dict = {"model": self.model, "prompt": self.prompt, "stream": self.stream, "options": self.options}
        return json.dumps(payload_dict)

    def to_dict(self):
        payload_dict = {"model": self.model, "prompt": self.prompt, "stream": self.stream, "options": self.options}
        return payload_dict

    def validate(self) -> Optional[str]:
        if not self.model:
            return "Model not found in data"
        return None

    def add_prompt(self, prompt: str):
        self.prompt = prompt
