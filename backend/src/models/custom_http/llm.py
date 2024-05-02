"""
LLM API model client implementation
"""

import json
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import requests
from langchain.llms.base import LLM
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from sseclient import SSEClient
from urllib.parse import urljoin
from typing import Any, Dict, Iterator, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from payload import PayloadFactory


class SSEManager:
    def __init__(self, base_url, endpoint, headers=None, max_retries=3, timeout=600):
        self.base_url = base_url
        self.endpoint = endpoint
        self.full_url = urljoin(self.base_url, self.endpoint)
        self.headers = headers if headers is not None else {}
        self.max_retries = max_retries
        self.timeout = timeout

    def post_http_request(self, url, json, stream, headers) -> requests.Response:
        return requests.post(url, json=json, stream=stream, headers=headers)

    def stream(self, payload):
        with requests.Session() as session:
            # session.mount(self.full_url, HTTPAdapter(max_retries=self.max_retries))
            self.headers["Content-Type"] = "application/json"

            response = session.post(
                self.full_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=self.timeout,
                stream=True,
            )
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    yield chunk

        # response = self.post_http_request(self.full_url, payload, stream=True, headers=self.headers)
        # for chunk in response.iter_content(chunk_size=128):
        #     if chunk:
        #         yield chunk

    def send_request(self, payload):
        """Send a simple HTTP POST request without streaming."""
        with requests.Session() as session:
            session.mount(self.base_url, HTTPAdapter(max_retries=self.max_retries))
            response = session.post(
                self.full_url,
                headers=self.headers,
                data=payload,
                timeout=self.timeout,
            )
            return response.text


class LLMAPI(LLM):
    """A wrapper for LLM API client.

    Example:
        .. code-block:: python

            llm = LLMAPI(
                host_name="http://localhost:8000",
                endpoint="/api/v1/generate",
                params = {"n_predict": 300, "temp": 0.2}
            )
    """

    llm_type: str = "ollama"
    streaming: bool = False
    host_name: str = "http://localhost:8000"
    endpoint: str = "/generate"  # Default endpoint
    request_timeout: Optional[Union[float, Tuple[float, float]]] = 600
    max_retries: int = 3
    params: Dict[str, Any] = Field(default_factory=dict)

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the LLM API model and return the output.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.
        Returns:
            The generated text.
        Example:
            .. code-block:: python
                llm = LLMAPI(
                    host_name="http://localhost:8000",
                    params = {"n_predict": 300, "temp": 0.2}
                )
                llm("This is a prompt.")
        """

        self.params["stop"] = stop or []
        payload = PayloadFactory().create_payload(model_type=self.llm_type, prompt=prompt, **self.params)
        # payload = json.dumps({self.prompt_key: prompt, "params": self.params})
        headers = {"Content-Type": "application/json"}
        sse_manager = SSEManager(
            base_url=self.host_name,
            endpoint=self.endpoint,
            headers=headers,
            max_retries=self.max_retries,
            timeout=self.request_timeout,
        )
        data = sse_manager.send_request(payload.to_json())
        return json.loads(data)["response"]

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the output from the LLM API model.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.
            run_manager: The run manager to handle the output.
            **kwargs: Additional arguments.
        Yields:
            The generated text.
        Example:
            .. code-block:: python
                llm = LLMAPI(
                    host_name="http://localhost:8000",
                    params = {"n_predict": 300, "temp": 0.2},
                    stream=True,
                    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
                )
                llm("This is a prompt.")
        """
        self.params["stream"] = True
        self.params["stop"] = stop or []
        payload = PayloadFactory().create_payload(model_type=self.llm_type, prompt=prompt, **self.params)
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
        sse_manager = SSEManager(
            base_url=self.host_name,
            endpoint=self.endpoint,
            headers=headers,
            max_retries=self.max_retries,
            timeout=self.request_timeout,
        )
        for data in sse_manager.stream(payload.to_dict()):
            try:
                data = json.loads(data.decode("utf-8"))  # Use json.loads to parse JSON correctly
                chunk = GenerationChunk(text=data["response"])
                if run_manager:
                    run_manager.on_llm_new_token(chunk.text, chunk=chunk)
                yield chunk
            except json.JSONDecodeError:
                yield GenerationChunk(text="")

    async def _astream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ):
        """Stream data from SSE and handle events using the provided callback manager."""
        # self.headers["Accept"] = "text/event-stream"
        import aiohttp

        headers = {"Content-Type": "application/json"}

        sse_manager = SSEManager(
            base_url=self.host_name,
            endpoint=self.endpoint,
            headers=headers,
            max_retries=self.max_retries,
            timeout=self.request_timeout,
        )
        self.params["stream"] = True
        self.params["stop"] = stop or []
        payload = PayloadFactory().create_payload(model_type=self.llm_type, prompt=prompt, **self.params).to_dict()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                sse_manager.full_url,
                headers=headers,
                json=payload,
            ) as response:
                async for data in self._stream_response(response):
                    chunk = GenerationChunk(text=data)
                    #  TODO: Implement callback manager
                    # if run_manager is not None:
                    #     run_manager.on_llm_new_token(chunk.text, chunk=chunk)
                    yield chunk

    async def _stream_response(self, response):
        async for line in response.content:
            try:
                json_line = json.loads(line.decode())
                yield json_line["response"]
            except json.JSONDecodeError:
                continue  # JSON 디코딩 오류 처리
            except Exception as e:
                print("error", e)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"host_name": self.host_name, "endpoint": self.endpoint}, **self.params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "llm-api"


async def main():
    llm = LLMAPI(
        llm_type="ollama",
        host_name="http://localhost:11434",
        endpoint="/api/generate",
        request_timeout=600,
        max_retries=3,
        params={
            "model": "deepseek-coder:6.7b",
            # "num_predict": 300,
        },
    )
    from langchain.chains import LLMChain, LLMMathChain, TransformChain, SequentialChain
    from langchain_core.runnables import RunnablePassthrough
    from langchain.prompts import PromptTemplate

    def transform_func(inputs: dict) -> dict:
        import re

        text = inputs["text"]

        # replace multiple new lines and multiple spaces with a single one
        text = re.sub(r"(\r\n|\r|\n){2,}", r"\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        return {"output_text": text}

    clean_extra_spaces_chain = TransformChain(
        input_variables=["text"], output_variables=["output_text"], transform=transform_func
    )
    template = """Paraphrase this text:

    {output_text}

    In the style of a {style}.

    Paraphrase: """
    from langchain.chains import LLMChain, LLMMathChain, TransformChain, SequentialChain

    prompt = PromptTemplate(input_variables=["style", "output_text"], template=template)
    style_paraphrase_chain = LLMChain(llm=llm, prompt=prompt, output_key="final_output")

    sequential_chain = SequentialChain(
        chains=[clean_extra_spaces_chain, style_paraphrase_chain],
        input_variables=["text", "style"],
        output_variables=["final_output"],
    )
    input_text = """
    Chains allow us to combine multiple 


    components together to create a single, coherent application. 

    For example, we can create a chain that takes user input,       format it with a PromptTemplate, 

    and then passes the formatted response to an LLM. We can build more complex chains by combining     multiple chains together, or by 


    combining chains with other components.
    """
    print("=" * 30)
    print(sequential_chain.run({"text": input_text, "style": "a 90s rapper"}))
    print("=" * 30)
    llm_math = LLMMathChain(llm=llm, verbose=True)
    print("=" * 30)
    print(llm_math.run("What is 13 raised to the .3432 power?"))
    print("=" * 30)
    print(llm_math.prompt.template)
    # # 프로그래밍 언어의 특정 기능에 대한 설명을 요청하는 템플릿
    # prompt_template_feature_description = "Explain the {feature} feature in {language}."

    # # 설명된 기능을 사용하는 코드 예제를 요청하는 템플릿
    # prompt_template_code_example = "Give me an example of using {feature} in {language}."

    # # 파이프라인 구성
    # chain = (
    #     PromptTemplate.from_template(prompt_template_feature_description)
    #     | llm  # 첫 번째 LLM 호출: 기능에 대한 설명을 요청
    #     | {"feature": RunnablePassthrough(), "language": RunnablePassthrough()}  # 받은 데이터를 다음 단계로 전달
    #     | PromptTemplate.from_template(prompt_template_code_example)
    #     | llm  # 두 번째 LLM 호출: 코드 예제를 요청
    # )
    # for chunk in chain.stream({"feature": "decorators", "language": "Python"}):
    #     print(chunk, flush=True, end="")

    # for event in llm.stream("write python loop code example please!"):
    #     print(event, flush=True, end="")
    # # async for event in llm.astream("write python loop code example please!"):
    # #     print(event, flush=True, end="")


# async def _stream_response(response):
#     async for line in response.content:
#         try:
#             json_line = json.loads(line.decode())
#             yield json_line["response"]
#         except json.JSONDecodeError:
#             continue  # JSON 디코딩 오류 처리
# async def main():
#     url = "http://localhost:11434/api/generate"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "model": "deepseek-coder:6.7b",
#         "prompt": "hi",
#         "stream": True,
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#             url,
#             headers=headers,
#             json=payload,
#         ) as response:
#             if response.status != 200:
#                 # 처리할 수 있는 에러 처리 로직 추가
#                 print(response)
#                 return
#             async for data in _stream_response(response):
#                 print(data)


if __name__ == "__main__":
    import asyncio
    import json

    asyncio.run(main())
