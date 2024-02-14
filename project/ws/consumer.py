from fastapi import WebSocket


class ConnectionManager:
    # def __init__(self):
    #     self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        # self.active_connections.remove(websocket)
        pass

    async def broadcast(self, text: str, username: str, created_at: str):
        # await self.add_message_to_db(text, username)
        # for connection in self.active_connections:
        #     await connection.send_json({'username': username,
        #                                 'text': text,
        #                                 'created_at': created_at})
        pass
    # @staticmethod
    # async def add_message_to_db(text: str, username: str):
    #     async with async_session_maker() as session:
    #         user = await session.execute(select(User).where(User.username == username))
    #         user = user.scalar_one()
    #         message = Message(user=user, text=text, username=username)
    #         session.add(message)
    #         await session.commit()


manager = ConnectionManager()
