from fastapi import WebSocket, WebSocketDisconnect

from . import ws_router
from ..bot.openai_sales import Chatbot


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    chatbot = Chatbot()
    try:
        while True:
            data = await websocket.receive_json()
            if "audio" not in data.keys():
                chatbot.set_settings(data)
            else:
                response = chatbot.ask(data)
                await websocket.send_json(response)
    except WebSocketDisconnect:
        pass

