from typing import Dict, Type
import os, sys

sys.path.append(__file__)
from .base import CommunicationStrategy
from .st_openai import OpenAIStrategy
from .st_https import HttpServiceStrategy
from .st_ollama import OllamaHTTPStrategy


class StrategyFactory:
    strategies: Dict[str, Type[CommunicationStrategy]] = {
        "OPENAI": OpenAIStrategy,
        "REMOTE": HttpServiceStrategy,
        "OLLAMA": OllamaHTTPStrategy,
    }

    @staticmethod
    async def get_strategy(name: str) -> CommunicationStrategy:
        strategy = StrategyFactory.strategies.get(name)
        if not strategy:
            raise ValueError(f"Strategy '{name}' not found")
        return strategy
