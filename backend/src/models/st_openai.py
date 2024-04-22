from .base import CommunicationStrategy
from openai import AsyncOpenAI
from typing import Dict, AsyncGenerator
import uuid
import asyncio


class OpenAIStrategy(CommunicationStrategy):
    def __init__(self, **kwargs):
        super().__init__()
        print("kwargs", kwargs)
        self.kwargs = kwargs
        self.client = AsyncOpenAI(api_key=self.kwargs["api_key"])

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
    #     all_content = ""

    #     async for chunk in response:
    #         print("chunk", chunk)
    #         # content = chunk.choices[0].message["content"] if chunk.choices[0].message else ""
    #         content = chunk.choices[0].delta.content
    #         if content:
    #             all_content += content
    #             yield {
    #                 "id": str(uuid.uuid4()),
    #                 "content": all_content,
    #                 "is_last": chunk.choices[0].finish_reason == "stop",
    #             }
    #         else:
    #             if chunk.choices[0].finish_reason == "stop":
    #                 yield {
    #                     "id": str(uuid.uuid4()),
    #                     "content": all_content,
    #                     "is_last": True,
    #                 }

    async def execute(self, data: Dict, cancel_signal: asyncio.Event = None) -> AsyncGenerator[Dict, None]:
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
            None,
        ]  # Example content

        async def response_generator():
            import time

            for content in response:
                time.sleep(0.5)
                yield content

        id = str(eval(data["message"])["id"])
        async for content in response_generator():
            if cancel_signal and cancel_signal.is_set():
                cancel_signal.clear()
                print("Cancel signal received")

                break  # 취소 신호가 설정되면 반복문 종료
            print(all_content)
            if content:
                all_content += content
                yield {"id": id, "content": all_content, "is_last": False}
            elif content is None:
                yield {"id": id, "content": all_content, "is_last": True}
