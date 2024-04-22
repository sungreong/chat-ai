from .base import CommunicationStrategy
from typing import Dict, AsyncGenerator
import uuid


class HttpServiceStrategy(CommunicationStrategy):
    def __init__(self, **kwargs):
        super().__init__()

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
