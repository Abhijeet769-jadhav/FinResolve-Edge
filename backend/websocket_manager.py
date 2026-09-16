import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("finresolve.websocket")

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Any):
        if not self.active_connections:
            return
        
        message = json.dumps({
            "type": event_type,
            "data": data
        }, default=str)

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to client, marking disconnected: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

ws_manager = WebSocketManager()
