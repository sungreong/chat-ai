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
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


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
        llm = ChatOllama(
            base_url=self.url,
            model=payload["model"],
            temperature=payload["options"].get("temperature", 0.0),
            num_predict=payload["options"].get("num_predict", 200),
            top_p=payload["options"].get("top_p", 1.0),
            top_k=payload["options"].get("top_k", 50),
            stop=payload["options"].get("stop", []),
            timeout=10_000,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI bot."),
                ("human", "{user_input}"),
            ]
        )
        self.chain = prompt | llm

        async for json_data in self._generate_response(payload, cancel_signal):
            if cancel_signal and cancel_signal.is_set():
                cancel_signal.clear()
                print("Cancel signal received")
                break  # 취소 신호가 설정되면 루프 종료
            yield json_data

    async def _generate_response(self, payload, cancel_signal):
        print("langchain_community.chat_models.ChatOllama")
        all_content = ""

        if self.stream:
            async for chunks in self.chain.astream({"user_input": payload["prompt"]}):
                if cancel_signal.is_set():
                    return
                all_content += chunks.content
                yield {"id": payload["id"], "content": all_content, "is_last": False}
            yield {"id": payload["id"], "content": all_content, "is_last": True}
        else:
            all_content = self.chain.invoke({"user_input": payload["prompt"]}).content
            yield {"id": payload["id"], "content": all_content, "is_last": True}
