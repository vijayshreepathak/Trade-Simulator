import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
import time

class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.logger = logging.getLogger(__name__)
        self._ws = None
        self._callbacks: List[Callable] = []
        self._connected = False
        self._task = None
        self._last_msg_time = 0

    async def connect(self) -> bool:
        """Connect to the WebSocket server."""
        try:
            if self._ws is not None:
                await self.close()
                
            self._ws = await websockets.connect(self.url)
            self._connected = True
            self._last_msg_time = time.time()
            
            # Start the message handler task
            self._task = asyncio.create_task(self._message_handler())
            
            self.logger.info(f"Connected to WebSocket at {self.url}")
            return True
        except Exception as e:
            self._connected = False
            self.logger.error(f"Failed to connect to WebSocket: {e}")
            raise

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            if self._task is not None:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
                self._task = None
                
            await self._ws.close()
            self._ws = None
            self._connected = False
            self.logger.info("Closed WebSocket connection")

    async def _message_handler(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            async for message in self._ws:
                try:
                    self._last_msg_time = time.time()
                    data = json.loads(message)
                    
                    # Create orderbook structure from Binance depth stream
                    if 'a' in data and 'b' in data:  # Binance depth format
                        orderbook_data = {
                            'asks': data.get('a', []),
                            'bids': data.get('b', []),
                            'timestamp': int(time.time() * 1000)
                        }
                        
                        # Notify callbacks with the orderbook data
                        for callback in self._callbacks:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(orderbook_data)
                                else:
                                    await asyncio.to_thread(callback, orderbook_data)
                            except Exception as e:
                                self.logger.error(f"Error in callback: {e}")
                except json.JSONDecodeError:
                    self.logger.error(f"Received invalid JSON: {message}")
                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket connection closed")
            self._connected = False
        except Exception as e:
            self.logger.error(f"Unexpected error in message handler: {e}")
            self._connected = False

    def register_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for orderbook updates."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            self.logger.debug(f"Registered new callback, total callbacks: {len(self._callbacks)}")

    def unregister_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _process_orderbook(self, data: Dict) -> Dict:
        """Process and validate orderbook data."""
        try:
            # Support both Binance full and diff depth stream formats
            asks = data.get("asks") or data.get("a") or []
            bids = data.get("bids") or data.get("b") or []
            processed_data = {
                "timestamp": datetime.utcnow(),
                "exchange": "Binance",
                "symbol": "BTCUSDT",
                "asks": [[float(price), float(size)] for price, size in asks],
                "bids": [[float(price), float(size)] for price, size in bids]
            }
            # If both bids and asks are empty, skip
            if not processed_data["bids"] and not processed_data["asks"]:
                raise ValueError("No bids or asks in message")
            return processed_data
        except Exception as e:
            self.logger.error(f"Error processing orderbook data: {e}")
            raise

    async def receive_message(self) -> str:
        """Receive a message from the WebSocket."""
        if not self._ws:
            raise ConnectionError("WebSocket is not connected")
        return await self._ws.recv()

    async def send_heartbeat(self):
        """Send a heartbeat message to keep the connection alive."""
        if not self._ws:
            raise ConnectionError("WebSocket is not connected")
        await self._ws.send('{"type": "ping"}')

    async def cleanup(self):
        """Clean up resources and close the connection."""
        await self.close()

    def is_connected(self) -> bool:
        """Check if the WebSocket is connected."""
        # Also check if we've received a message in the last 30 seconds
        if not self._connected:
            return False
            
        # If no message in 30 seconds, consider connection stale
        if time.time() - self._last_msg_time > 30:
            self.logger.warning("No message received in last 30 seconds, connection considered stale")
            return False
            
        return True 