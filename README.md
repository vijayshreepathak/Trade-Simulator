Trade Simulator
A professional-grade trade simulation tool for cryptocurrency traders featuring real-time market data visualization, slippage modeling, and cost analysis.

🚀 Features
Real-time Market Data: Connects to exchange WebSockets (Binance, Coinbase, etc.) to receive and display live order book data.

Advanced Trade Cost Analysis: Calculates potential slippage, market impact, and exchange fees before you commit to a trade.

Maker/Taker Prediction: Intelligently estimates whether an order of a given size is likely to be a maker (adding liquidity) or a taker (removing liquidity).

Modern & Intuitive UI: A clean user interface built with PySide6, featuring color-coded metrics for quick and easy analysis.

Multi-Exchange Support: Designed to be extensible for major exchanges, providing a consistent simulation experience across different platforms.

🏗️ System Architecture
This diagram illustrates the components and data flow of the Trade Simulator application. The UI, built with PySide6, captures user input and displays results. The core logic is managed by a controller that interfaces with a WebSocket client for live data and a simulation engine for calculations.

graph TD
    subgraph UserInterface [User Interface (PySide6)]
        direction LR
        A[Input Panel</br>Exchange, Pair, Size, Fees]
        B[Real-time Display</br>Order Book, Metrics]
        C[Control Buttons</br>"Simulate Trade"]
    end

    subgraph CoreApplication [Core Application Logic]
        direction TB
        D(main.py</br>App Entry Point)
        E(TradeController</br>Manages State & Events)
        F(SimulationEngine</br>Calculates Slippage, Impact, Costs)
    end

    subgraph DataLayer [Data Layer]
        direction TB
        G(WebSocketClient</br>Connects to Exchange APIs)
        H(DataParser</br>Normalizes Order Book Data)
    end

    subgraph ExternalServices [External Services]
        direction LR
        I([Binance WebSocket])
        J([Coinbase WebSocket])
        K([Kraken WebSocket])
    end

    %% Connections
    A -- User Input --> E
    C -- "onClick" --> E
    E -- "Start Simulation" --> F
    E -- "Start/Stop Feed" --> G
    G -- "Connects to" --> I
    G -- "Connects to" --> J
    G -- "Connects to" --> K

    I -- Raw Data --> G
    J -- Raw Data --> G
    K -- Raw Data --> G

    G -- Raw JSON --> H
    H -- Parsed Order Book --> F
    F -- Simulation Results --> E
    E -- Updates UI --> B

    D -- "Initializes" --> E
    E -- "Owns/Manages" --> A & B & C

🖼️ Screenshot
🛠 Installation
Prerequisites
Python 3.9 or higher

An operating system that supports PySide6 (Windows, macOS, Linux)

Setup Instructions
Clone or download the repository:

git clone https://github.com/your-username/trade-simulator.git
cd trade-simulator

Create and activate a virtual environment:

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.venv\Scripts\activate

Install the required dependencies:

pip install -r requirements.txt

Run the application:

python main.py

💡 Usage
Launch the application using the instructions above.

Select the desired Exchange and Trading Pair from the dropdown menus.

Enter your desired Order Size in USD.

Adjust the Volatility slider (0 to 1) to model different market conditions.

Choose your estimated Fee Tier to ensure accurate cost calculation.

Click "Connect to Feed" to start receiving live order book data.

Click "Simulate Trade" to compute and display the results.

Analyze the metrics for Slippage, Market Impact, Fees, and the Maker/Taker prediction.

🧠 Key Components
Trade Simulation Engine: Contains the core mathematical models to estimate market impact (based on the Almgren–Chriss framework), slippage, and execution probabilities.

WebSocket Client: A robust client that interfaces with major exchange APIs for receiving high-frequency, real-time order book data.

User Interface (PySide6): A responsive and modern GUI that provides an intuitive way for users to interact with the simulator and visualize data.

⚙️ Technical Details
The simulator provides pre-trade analytics by modeling how an order would interact with the live order book.

Slippage: Calculated as the percentage difference between the expected execution price (based on the current order book) and the actual average price after your order "walks the book."

Market Impact: Modeled to estimate how the price might shift as a direct result of your order's size removing liquidity.

Execution Costs: The total estimated cost of the trade, combining slippage, exchange fees (based on the selected tier), and market impact.

📁 Project Structure
trade-simulator/
├── docs/                # Documentation and screenshots
├── src/
│   ├── models/          # Simulation models (simulation_engine.py)
│   ├── ui/              # UI components (main_window.py, style.qss)
│   └── websocket/       # WebSocket data client (client.py)
├── tests/               # Unit and integration tests
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies

👩‍💻 Author
Developed by Vijayshree
