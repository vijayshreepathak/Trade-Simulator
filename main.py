import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop
from src.ui.main_window import MainWindow
from src.websocket.client import WebSocketClient
from src.models.market_impact import AlmgrenChrissModel
from src.models.slippage import SlippageModel
from src.models.maker_taker import MakerTakerModel
from src.utils.logging_config import setup_logging
import logging


class ReconnectingWebSocketClient(WebSocketClient):
    def __init__(self, url, reconnect_interval=5):
        super().__init__(url)
        self.reconnect_interval = reconnect_interval
        self.should_reconnect = True
        self.is_connecting = False
        self._callbacks = []
    
    async def connect_with_retry(self):
        if self.is_connecting:
            return False
            
        self.is_connecting = True
        try:
            while self.should_reconnect:
                try:
                    await self.connect()
                    logging.info("WebSocket connected successfully")
                    self.is_connecting = False
                    return True
                except Exception as e:
                    logging.error(f"WebSocket connection failed: {e}")
                    logging.info(f"Attempting to reconnect in {self.reconnect_interval} seconds...")
                    await asyncio.sleep(self.reconnect_interval)
        finally:
            self.is_connecting = False
        return False
    
    def is_connected(self):
        if hasattr(self, "_ws") and self._ws and not self._ws.closed:
            return True
        return False
        
    def register_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)


def main():
    try:
        # Set up logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Trade Simulator")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Trade Simulator")
        app.setApplicationVersion("1.0.0")
        
        # Initialize models
        logger.info("Initializing models...")
        market_impact_model = AlmgrenChrissModel()
        slippage_model = SlippageModel()
        maker_taker_model = MakerTakerModel()
        
        # Initialize WebSocket client
        logger.info("Initializing WebSocket client...")
        ws_client = ReconnectingWebSocketClient(
            url="wss://stream.binance.com:9443/ws/btcusdt@depth"
        )
        
        # Setup qasync
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        # Initialize and show main window
        logger.info("Creating main window...")
        window = MainWindow(
            market_impact_model=market_impact_model,
            slippage_model=slippage_model,
            maker_taker_model=maker_taker_model,
            ws_client=ws_client
        )
        window.show()
        
        # Setup WebSocket connection in the event loop
        async def start_ws_connection():
            logger.info("Connecting to WebSocket...")
            await ws_client.connect_with_retry()
            
        # Setup periodic connection check
        async def check_connection():
            while True:
                await asyncio.sleep(15)  # Check every 15 seconds
                if not ws_client.is_connected() and not ws_client.is_connecting:
                    logger.warning("WebSocket disconnected, attempting to reconnect...")
                    asyncio.create_task(ws_client.connect_with_retry())
        
        # Start connection tasks
        loop.create_task(start_ws_connection())
        loop.create_task(check_connection())
        
        logger.info("Application started successfully")
        with loop:
            return loop.run_forever()
            
    except Exception as e:
        logging.error(f"Failed to initialize application: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"Application terminated with error: {e}", exc_info=True)
        sys.exit(1)
