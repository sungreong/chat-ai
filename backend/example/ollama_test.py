import asyncio
from ollama import AsyncClient

url = "http://localhost:11434"


async def chat():
    message = {"role": "user", "content": "Why is the sky blue?"}
    async for part in await AsyncClient(url).chat(model="deepseek-coder:6.7b", messages=[message], stream=True):
        print(part)
        print(part["message"]["content"], end="", flush=True)


asyncio.run(chat())


# # Get the existing event loop or create one if not exist
# loop = asyncio.get_event_loop()

# # Run the chat coroutine within the existing loop
# loop.run_until_complete(chat())
