from typing import AsyncGenerator, NoReturn

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Depends, HTTPException, APIRouter, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI
import os, sys
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(__file__)
from src.models import StrategyFactory

load_dotenv()

app = FastAPI()
# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # 프론트엔드 서버의 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
router = APIRouter()

# 사용자별 모델 설정을 저장하는 딕셔너리
# 사용자 정보를 저장하는 딕셔너리
user_db: Dict[str, Dict] = {}
user_db["srlee"] = {
    "model_type": "OPENAI",
    "parameters": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-3.5-turbo",
    },
}
from pydantic import BaseModel
from pydantic import BaseModel, Field


# 사용자 모델 설정 파라미터를 정의하는 Pydantic 모델
class UserModelConfig(BaseModel):
    model_type: str
    parameters: Dict = Field(...)


# 사용자 정보를 정의하는 Pydantic 모델
class UserInfo(BaseModel):
    model_config: UserModelConfig


# 사용자 정보를 정의하는 Pydantic 모델
# class User(BaseModel):
#     name: str
#     type: Dict = Field(...)

# @app.post("/users/{user_id}")
# async def create_user(user_id: str, user: User):
#     # if user_id in user_db:
#     #     raise HTTPException(status_code=400, detail="User already exists")
#     print(user)
#     user_db[user_id] = user.dict()
#     return {"user_id": user_id, "user_info": user_db[user_id]}


@router.post("/users/{user_id}")
async def save_user_info(user_id: str, user_info: UserModelConfig) -> UserInfo:
    """
    사용자 정보를 저장합니다.
    """
    # 사용자 ID를 기반으로 사용자 정보를 user_db에 저장

    user_db[user_id] = user_info.dict()
    return {"message": "User info saved", "user_id": user_id, "user_info": user_info}
    # {"message": "User info saved", "user_id": user_id, "user_info": user_info}


@router.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """
    특정 사용자의 정보를 반환합니다.
    """
    if user_id not in user_db:
        raise HTTPException(status_code=404, detail="User not found")
    print({"user_id": user_id, "user_info": user_db[user_id]})
    return {"user_id": user_id, "user_info": user_db[user_id]}


import asyncio

cancel_signal = asyncio.Event()


@router.post("/cancel/{action}")
async def update_cancel_signal(action: str):
    print("update_cancel_signal")
    global cancel_signal
    if action == "set":
        cancel_signal.set()
        return {"message": "cancelRequest"}
    elif action == "clear":
        cancel_signal.clear()
        return {"message": "Cancel signal cleared."}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")


from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def is_connected(self, websocket: WebSocket):
        return websocket in self.active_connections

    async def disconnect(self, websocket: WebSocket):
        # Check if the websocket is in the list of active connections
        if self.is_connected(websocket):
            # Try to close the websocket if it hasn't been closed already
            try:
                await websocket.close()
            except RuntimeError as e:
                # Handle the case where the websocket might already be closed
                print(f"Attempted to close an already closed websocket: {e}")
            finally:
                # Ensure the websocket is removed from the list of active connections
                self.active_connections.remove(websocket)


manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> NoReturn:
    """
    Websocket for AI responses
    """

    # await websocket.accept()
    await manager.connect(websocket)

    strategy_dict = user_db.get(user_id, {})
    if len(strategy_dict) == 0:
        await websocket.send_text(f"Error: Strategy not found for user {user_id}.")
        return
    strategycls = await StrategyFactory.get_strategy(strategy_dict["model_type"])
    strategy = strategycls(**strategy_dict["parameters"])

    async def cancel_task():
        print("cancel_signal set")
        cancel_signal.set()
        await websocket.send_text("Task canceled.")

    try:
        while True:
            message = await websocket.receive_text()
            if message == "cancelRequest":
                asyncio.create_task(cancel_task())
                break
            else:
                response_generator = strategy.execute({"message": message}, cancel_signal)
                async for json_data in response_generator:
                    if cancel_signal.is_set():
                        cancel_signal.clear()
                        break
                    await websocket.send_json(json_data)
    except WebSocketDisconnect:
        cancel_signal.set()
    except Exception as e:
        cancel_signal.set()
        print(f"WebSocket error: {e}")
    finally:
        cancel_signal.clear()
        # await websocket.close()
        await manager.disconnect(websocket)


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        # log_level="debug",
        log_level="info",
        reload=True,
    )
