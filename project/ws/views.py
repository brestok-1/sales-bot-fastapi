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
            signal = data['type']
            if signal == 'set_settings':
                chatbot.set_settings(data['data'])
                persona = chatbot.generate_random_persona()
                await websocket.send_json(persona)
            elif signal == 'asking':
                response = chatbot.ask(data['data'])
                await websocket.send_json(response)
    except WebSocketDisconnect:
        pass


