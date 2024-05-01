# from .base import CommunicationStrategy
from typing import Dict, AsyncGenerator
import uuid
import aiohttp
from .base import CommunicationStrategy
import aiohttp
import asyncio
import json
from copy import deepcopy

import requests
from typing import Dict, Generator
import re
from ollama import AsyncClient


class OllamaHTTPStrategy(CommunicationStrategy):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.url = self.kwargs["url"]
        if "stream" in self.kwargs:
            if isinstance(self.kwargs["stream"], str):
                self.stream = eval(self.kwargs["stream"].title())
            elif isinstance(self.kwargs["stream"], bool):
                self.stream = self.kwargs["stream"]
            else:
                self.stream = False
        self.kwargs["stop"] = [i.strip() for i in kwargs.get("stop").split(",")]
        self.options = deepcopy(kwargs)
        for key in ["url", "stream", "model", "apiToken"]:
            if key in self.options:
                del self.options[key]

    async def execute(self, data: Dict, cancel_signal: asyncio.Event = None):
        print(data)

        if "model" not in self.kwargs:
            yield {"content": "Model not found in data", "is_last": True}
            return
        id = str(eval(data["message"])["id"])

        payload = {
            "model": self.kwargs.get("model", "llama2"),
            "id": id,
            "prompt": eval(data["message"])["question"],
            "stream": self.stream,
            "options": self.options,
        }

        async for json_data in self._generate_response(payload, cancel_signal):
            if cancel_signal and cancel_signal.is_set():
                cancel_signal.clear()
                print("Cancel signal received")
                break  # 취소 신호가 설정되면 루프 종료
            yield json_data

    async def _generate_response(self, payload, cancel_signal):
        message = {"role": "user", "content": payload["prompt"]}
        all_content = ""
        async for part in await AsyncClient(host=self.url).chat(
            model=payload["model"], messages=[message], stream=payload["stream"]
        ):
            if cancel_signal.is_set():
                return  # Immediate response to cancellation requests
            if part.get("done", False):
                # When the "done" flag is True, the message is considered complete
                yield {"id": payload["id"], "content": all_content, "is_last": True}
                continue
            else:
                all_content += part["message"]["content"]
                # When the "done" flag is False, the message is considered incomplete
                yield {"id": payload["id"], "content": all_content, "is_last": False}
            if self.stream:
                yield {"id": payload["id"], "content": all_content, "is_last": part["done"]}
            else:
                yield {"id": payload["id"], "content": part["message"]["content"], "is_last": part["done"]}
