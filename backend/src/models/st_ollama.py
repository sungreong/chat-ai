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

    # async def _generate_response(self, payload, cancel_signal):
    #     headers = {"Content-Type": "application/json"}
    #     response = requests.post(self.url, headers=headers, json=payload, stream=self.stream)

    #     if response.status_code != 200:
    #         yield {"content": response.text, "is_last": True}
    #     else:
    #         all_content = ""
    #         if self.stream:
    #             for chunk in response.iter_content(chunk_size=2048):
    #                 print(cancel_signal)
    #                 if cancel_signal and cancel_signal.is_set():
    #                     break  # 취소 신호가 설정되면 반복문 종료
    #                 if chunk:
    #                     decoded_chunk = chunk.decode()
    #                     try:
    #                         data_dict = json.loads(decoded_chunk)
    #                         response_value = data_dict["response"]
    #                         done_value = data_dict["done"]
    #                     except json.JSONDecodeError:
    #                         print("Error decoding chunk")
    #                         # 'response' 필드의 값을 추출하기 위한 정규 표현식
    #                         response_pattern = r'"response":\s*"([^"]*)"'
    #                         # 'done' 필드의 값을 추출하기 위한 정규 표현식
    #                         done_pattern = r'"done":\s*(true|false)'

    #                         # 'response' 필드 값 검색
    #                         response_match = re.search(response_pattern, decoded_chunk)
    #                         if response_match:
    #                             response_value = response_match.group(1)
    #                             print(f"Response: {response_value}")
    #                         else:
    #                             print("Response not found")

    #                         # 'done' 필드 값 검색
    #                         done_match = re.search(done_pattern, decoded_chunk)
    #                         if done_match:
    #                             done_value = done_match.group(1) == "true"  # boolean 변환
    #                             print(f"Done: {done_value}")
    #                         else:
    #                             print("Done field not found")
    #                     finally:
    #                         all_content += response_value
    #                     if done_value:
    #                         break
    #                     else:
    #                         yield {"id": str(uuid.uuid4()), "content": all_content, "is_last": False}

    #             yield {"id": str(uuid.uuid4()), "content": all_content, "is_last": True}
    #         else:
    #             result = response.json()
    #             yield {"id": str(uuid.uuid4()), "content": result["response"], "is_last": True}

    async def _generate_response(self, payload, cancel_signal):
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=headers, json=payload) as response:
                if response.status != 200:
                    yield {"content": await response.text(), "is_last": True}
                    return

                if self.stream:
                    all_content = ""
                    async for data, is_last in self._stream_response(response, cancel_signal):
                        all_content += data
                        yield {"id": payload["id"], "content": all_content, "is_last": is_last}
                else:
                    result = await response.json()
                    yield {"id": payload["id"], "content": result["response"], "is_last": True}

    async def _stream_response(self, response, cancel_signal):
        async for line in response.content:
            if cancel_signal and cancel_signal.is_set():
                return  # 취소 신호가 발생하면 반복 중지
            try:
                json_line = json.loads(line.decode())
                yield json_line["response"], json_line.get("done", False)
            except json.JSONDecodeError:
                continue  # JSON 디코딩 오류 처리


# async def fetch(url, data):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"}) as response:
#             print("Status:", response.status)
#             print("Content-type:", response.headers["content-type"])

#             body = await response.text()
#             # print()
#             print("Body:", eval(body)["response"])


# async def main():
#     url = "http://localhost:11434/api/generate"
#     data = {
#         "model": "deepseek-coder:6.7b",
#         "prompt": "\[INST\] why is the sky blue? \[/INST\]",
#         "raw": False,
#         "stream": True,
#     }

#     await fetch(url, data)


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
