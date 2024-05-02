from .base import CommunicationStrategy
from .custom_http import LLMAPI
from .custom_http.payload import PayloadFactory
from typing import Dict, AsyncGenerator
import uuid
from copy import deepcopy
import asyncio
from langchain_core.prompts import ChatPromptTemplate


class HttpServiceStrategy(CommunicationStrategy):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.hostname = self.kwargs["hostname"]
        self.endpoint = self.kwargs["endpoint"]
        self.llm_type = self.kwargs["llm_type"]
        if "stream" in self.kwargs:
            if isinstance(self.kwargs["stream"], str):
                self.stream = eval(self.kwargs["stream"].title())
            elif isinstance(self.kwargs["stream"], bool):
                self.stream = self.kwargs["stream"]
            else:
                self.stream = False
        self.kwargs["stop"] = [i.strip() for i in kwargs.get("stop").split(",")]
        self.options = deepcopy(kwargs)
        for key in ["hostname", "endpoint", "llm_type", "apiToken"]:
            if key in self.options:
                del self.options[key]

    async def execute(self, data: Dict, cancel_signal: asyncio.Event = None):
        # payload_cls = self.factory.create_payload(model_type=self.llm_type, prompt="")
        # payload_cls.add_prompt(eval(data["message"])["question"])
        id = str(eval(data["message"])["id"])
        payload = {
            "model": self.kwargs.get("model", "llama2"),
            "id": id,
            "prompt": eval(data["message"])["question"],
            "stream": self.stream,
            "options": self.options,
        }
        llm = LLMAPI(host_name=self.hostname, endpoint=self.endpoint, params=self.options)
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
        all_content = ""

        if self.stream:
            async for chunks in self.chain.astream({"user_input": payload["prompt"]}):
                if cancel_signal.is_set():
                    return
                all_content += chunks
                yield {"id": payload["id"], "content": all_content, "is_last": False}
            yield {"id": payload["id"], "content": all_content, "is_last": True}
        else:
            all_content = self.chain.invoke({"user_input": payload["prompt"]})
            yield {"id": payload["id"], "content": all_content, "is_last": True}

    # async def execute(self, data: Dict) -> AsyncGenerator[Dict, None]:
    #     """
    #     Sample Response
    #     """
    #     all_content = ""
    #     response = [
    #         "# Hello, \n",
    #         "- how can I help you?\n",
    #         "```python\n",
    #         "import numpy as np\nimport pandas as pd\n",
    #         "```\n",
    #         "add new code\n",
    #         "```python\n",
    #         "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n",
    #         "```\n",
    #         "```javascript\n",
    #         "console.log('Hello, World!')\n",
    #         "```\n",
    #     ]  # Example content

    #     async def response_generator():
    #         import time

    #         for content in response:
    #             time.sleep(0.5)
    #             yield content

    #     id = str(uuid.uuid4())
    #     async for content in response_generator():
    #         if content:
    #             all_content += content
    #             yield {"id": id, "content": all_content}
