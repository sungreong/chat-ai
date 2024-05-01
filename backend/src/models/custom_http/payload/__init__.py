from .ollama import OllamaPayload
from .vllm import VllmPayload

from enum import Enum
from typing import Any


class ModelType(Enum):
    OLLAMA = "ollama"
    VLLM = "vllm"


class PayloadFactory:
    def __init__(self):
        # Payload 클래스의 매핑을 저장
        self.payload_classes = {"ollama": OllamaPayload, "vllm": VllmPayload}

    def create_payload(self, model_type: ModelType, prompt: str, **kwargs) -> Any:
        """
        Create and return a payload instance based on the model type.

        Args:
            model_type (ModelType): The type of model for which to create a payload.
            prompt (str): The prompt to be used for the payload.
            **kwargs: Additional arguments to pass to the payload constructor.

        Returns:
            An instance of OllamaPayload or VllmPayload.

        Raises:
            ValueError: If the model type is not supported.
        """
        payload_class = self.payload_classes.get(model_type)
        if payload_class is None:
            raise ValueError(f"Unsupported model type: {model_type}")
        return payload_class(prompt=prompt, **kwargs)
