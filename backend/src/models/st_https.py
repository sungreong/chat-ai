from .base import CommunicationStrategy
from .custom_http import LLMAPI
from .custom_http.payload import PayloadFactory
from typing import Dict, AsyncGenerator
import uuid
from copy import deepcopy
import asyncio


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
        for key in ["hostname", "endpoint", "llm_type", "stream", "model", "apiToken"]:
            if key in self.options:
                del self.options[key]
        self.factory = PayloadFactory()

    async def execute(self, data: Dict, cancel_signal: asyncio.Event = None):
        payload_cls = self.factory.create_payload(model_type=self.llm_type)
        payload_cls.add_prompt(eval(data["message"])["question"])
        id = str(eval(data["message"])["id"])
        payload = {
            "model": self.kwargs.get("model", "llama2"),
            "id": id,
            "prompt": eval(data["message"])["question"],
            "stream": self.stream,
            "options": self.options,
        }
        LLMAPI(hostname=self.hostname, endpoint=self.endpoint)

    # async def execute(self, data: Dict) -> AsyncGenerator[Dict, None]:
    #     response = await self.client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": "You are a helpful assistant, skilled in explaining complex concepts in simple terms.",
    #             },
    #             {
    #                 "role": "user",
    #                 "content": data["message"],
    #             },
    #         ],
    #         max_tokens=100,
    #         stream=True,
    #     )

    #     async for chunk in response:
    #         content = chunk.choices[0].message["content"] if chunk.choices[0].message else ""
    #         if content:
    #             yield {"id": str(uuid.uuid4()), "content": content}

    async def execute(self, data: Dict) -> AsyncGenerator[Dict, None]:
        """
        Sample Response
        """
        all_content = ""
        response = [
            "# Hello, \n",
            "- how can I help you?\n",
            "```python\n",
            "import numpy as np\nimport pandas as pd\n",
            "```\n",
            "add new code\n",
            "```python\n",
            "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n",
            "```\n",
            "```javascript\n",
            "console.log('Hello, World!')\n",
            "```\n",
        ]  # Example content

        async def response_generator():
            import time

            for content in response:
                time.sleep(0.5)
                yield content

        id = str(uuid.uuid4())
        async for content in response_generator():
            if content:
                all_content += content
                yield {"id": id, "content": all_content}
