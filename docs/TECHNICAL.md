# Trade Simulator - Technical Documentation

## Architecture Overview

The Trade Simulator is built with a modular architecture consisting of several key components:

1. **User Interface Layer** (PySide6/Qt)
2. **WebSocket Client** (Async websockets)
3. **Simulation Models** (Market impact, slippage, maker/taker prediction)
4. **Utility Services** (Logging, configuration)

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Trade Simulator                       │
└──────────────────────────┬─────────────────────────────────┘
                           │
        ┌──────────────────┴─────────────────┐
        ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│    UI Layer     │                  │  WebSocket      │
│  (PySide6/Qt)   │◄───────────────► │  Client         │◄─────► Crypto Exchange
└─────────────────┘                  └─────────────────┘        APIs
        │                                    │
        ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│  Trade Models   │                  │  Utility        │
│  & Calculations │                  │  Services       │
└─────────────────┘                  └─────────────────┘
```

## Components in Detail

### UI Layer (src/ui/main_window.py)

The UI is implemented using PySide6 (Qt for Python) and features:

- **Responsive Layout**: Adapts to different screen sizes
- **Modern Design**: Clean, professional styling with consistent color scheme
- **Real-time Updates**: Asynchronous updates from WebSocket
- **Input Controls**: Form inputs for trade parameters
- **Output Displays**: Result displays with color-coded metrics
- **Live Orderbook**: Real-time market depth visualization

#### UI Class Hierarchy

- `MainWindow`: Main application window
  - Input Panel: Trade parameter inputs
  - Output Panel: Simulation results
  - Orderbook Panel: Live market data

#### UI Styling

The UI utilizes a custom stylesheet with a consistent color palette:

```python
self.brand_colors = {
    'primary': '#6f42c1',        # Primary purple
    'secondary': '#3a1c71',      # Deeper purple
    'accent': '#8a67dd',         # Light purple
    'success': '#2ecc71',        # Green
    'warning': '#f39c12',        # Orange
    'danger': '#e74c3c',         # Red
    'neutral_dark': '#333333',   # Dark gray
    'neutral_light': '#f8f9fa',  # Light gray
    'text': '#444444',           # Text color
    'white': '#ffffff',          # White
    'bid': '#2a9d8f',            # Teal for bids
    'ask': '#e76f51'             # Coral for asks
}
```

### WebSocket Client (src/websocket/client.py)

The WebSocket client connects to cryptocurrency exchange APIs and:

- Establishes and maintains WebSocket connections
- Processes market data in real-time
- Handles connection failures with automatic reconnection
- Parses exchange-specific data formats
- Notifies the UI of updates through callbacks

#### WebSocket Implementation

```python
class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self._callbacks = []
        self._connected = False
        
    async def connect(self) -> bool:
        # Establishes WebSocket connection
        
    async def _message_handler(self) -> None:
        # Processes incoming messages
        
    def register_callback(self, callback):
        # Registers UI callbacks for updates
```

### Simulation Models (src/models/)

The simulator uses several mathematical models to estimate trade costs:

#### Market Impact Model (Almgren-Chriss)

Estimates how much a trade will move the market based on:
- Order size
- Market depth
- Volatility
- Time horizon

```python
class AlmgrenChrissModel:
    def estimate_market_impact(self, order_quantity, market_depth, time_horizon):
        # Calculates expected market impact
```

#### Slippage Model

Predicts the difference between expected and actual execution price:
- Uses regression techniques
- Considers order size relative to market depth
- Accounts for market volatility

#### Maker/Taker Model

Predicts the probability of orders being filled as maker vs. taker:
- Analyzes market conditions and spread
- Considers order size and volatility
- Predicts fee implications

### Threading and Performance

The application uses several techniques to ensure responsive performance:

1. **Asynchronous WebSocket Processing**: Uses Python's asyncio
2. **Thread-Safe UI Updates**: Prevents UI freezes during data processing
3. **Throttled Updates**: Limits update frequency to reduce CPU usage
4. **Efficient Data Structures**: Optimized data handling

## Data Flow

1. WebSocket client connects to exchange API
2. Real-time market data flows into the application
3. Data is processed by simulation models
4. UI is updated with calculated metrics and orderbook
5. User input triggers new calculations

## UI-to-Model Interaction

```
┌──────────────┐    Parameters     ┌─────────────┐
│              │───────────────── │              │
│     UI       │                   │   Models    │
│              │◄─────────────────│              │
└──────────────┘    Results        └─────────────┘
        ▲                                 ▲
        │                                 │
        │                                 │
        ▼                                 ▼
┌──────────────┐                  ┌─────────────┐
│  WebSocket   │◄────────────────►│  Exchange   │
│  Client      │     Data Flow    │  API        │
└──────────────┘                  └─────────────┘
```

## Error Handling

The application implements comprehensive error handling:

- WebSocket connection failures with automatic retry
- Data parsing errors with graceful fallbacks
- UI thread safety to prevent crashes
- Logging of errors for troubleshooting

## Performance Optimizations

- **Throttled UI Updates**: UI updates are limited to prevent excessive CPU usage
- **Efficient Processing**: Only essential data is processed and displayed
- **Memory Management**: Data history is limited to prevent memory leaks

## Future Enhancements

Planned technical improvements include:

1. **Additional Exchange Support**: More exchange APIs
2. **Enhanced Models**: More sophisticated pricing models
3. **Historical Backtesting**: Testing strategies against historical data
4. **Performance Profiling**: Further optimization of critical paths
5. **Multi-account Support**: Managing multiple trading accounts 