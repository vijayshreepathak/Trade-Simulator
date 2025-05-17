import asyncio
import pytest
from src.websocket.client import WebSocketClient
import logging
from unittest.mock import AsyncMock, patch

@pytest.fixture
def setup_logging():
    logging.basicConfig(level=logging.INFO)

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    mock = AsyncMock()
    mock.send = AsyncMock()
    mock.close = AsyncMock()
    mock.recv = AsyncMock()
    mock.open = True
    return mock

@pytest.fixture
def client():
    """Create a WebSocket client instance."""
    return WebSocketClient(
        url="wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP",
        reconnect_interval=1.0
    )

@pytest.mark.asyncio
async def test_websocket_connection(client, mock_websocket):
    """Test WebSocket connection establishment."""
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        assert client.is_connected()
        assert client.websocket == mock_websocket

@pytest.mark.asyncio
async def test_websocket_disconnection(client, mock_websocket):
    """Test WebSocket disconnection."""
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        await client.disconnect()
        assert not client.is_connected()
        mock_websocket.close.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_message_handling(client, mock_websocket):
    """Test WebSocket message handling."""
    test_message = '{"type": "orderbook", "data": {"bids": [[50000, 1.0]], "asks": [[50100, 1.0]]}}'
    mock_websocket.recv.return_value = test_message
    
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        message = await client.receive_message()
        assert message == test_message

@pytest.mark.asyncio
async def test_websocket_reconnection(client, mock_websocket):
    """Test WebSocket reconnection on connection loss."""
    connect_calls = 0
    
    async def mock_connect(*args, **kwargs):
        nonlocal connect_calls
        connect_calls += 1
        if connect_calls == 1:
            raise ConnectionError("Connection lost")
        return mock_websocket
    
    with patch('websockets.connect', side_effect=mock_connect):
        # First connection attempt should fail
        with pytest.raises(ConnectionError):
            await client.connect()
        
        # Second connection attempt should succeed
        await client.connect()
        assert client.is_connected()
        assert connect_calls == 2

@pytest.mark.asyncio
async def test_websocket_heartbeat(client, mock_websocket):
    """Test WebSocket heartbeat mechanism."""
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        await client.send_heartbeat()
        mock_websocket.send.assert_called_with('{"type": "ping"}')

@pytest.mark.asyncio
async def test_websocket_error_handling(client, mock_websocket):
    """Test WebSocket error handling."""
    mock_websocket.recv.side_effect = Exception("Test error")
    
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        with pytest.raises(Exception):
            await client.receive_message()

@pytest.mark.asyncio
async def test_websocket_cleanup(client, mock_websocket):
    """Test WebSocket cleanup on shutdown."""
    with patch('websockets.connect', return_value=mock_websocket):
        await client.connect()
        await client.cleanup()
        assert not client.is_connected()
        mock_websocket.close.assert_called_once() 