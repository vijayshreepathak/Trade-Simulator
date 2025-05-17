from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QGroupBox, QFormLayout, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QBrush, QGradient
import logging
import datetime

class MainWindow(QMainWindow):
    def __init__(self, market_impact_model, slippage_model, maker_taker_model, ws_client):
        super().__init__()
        self.market_impact_model = market_impact_model
        self.slippage_model = slippage_model
        self.maker_taker_model = maker_taker_model
        self.ws_client = ws_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.current_orderbook = None
        self.processing_time = 0
        self.last_update_time = None
        self.connected = False
        self._update_in_progress = False
        
        # Define brand colors for consistent UI
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
        
        self.setWindowTitle("Trade Simulator by Vijayshree")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(self._get_main_stylesheet())
        self._init_ui()

    def _get_main_stylesheet(self):
        """Return a professional stylesheet for the application"""
        return f"""
        QMainWindow {{
            background: {self.brand_colors['neutral_light']};
        }}
        QGroupBox {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-weight: bold;
            border: 1px solid #d0d5e0;
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 12px;
            background: {self.brand_colors['white']};
            color: {self.brand_colors['primary']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        QLabel {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            color: {self.brand_colors['text']};
            padding: 2px;
        }}
        QDoubleSpinBox, QComboBox {{
            border: 1px solid #d0d5e0;
            border-radius: 4px;
            padding: 5px;
            background: {self.brand_colors['neutral_light']};
            min-height: 20px;
            color: {self.brand_colors['text']};
        }}
        QDoubleSpinBox:hover, QComboBox:hover {{
            border: 1px solid {self.brand_colors['accent']};
        }}
        QDoubleSpinBox:focus, QComboBox:focus {{
            border: 1px solid {self.brand_colors['primary']};
            background: white;
        }}
        QPushButton {{
            background: {self.brand_colors['primary']};
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            border: none;
        }}
        QPushButton:hover {{
            background: {self.brand_colors['secondary']};
        }}
        QPushButton:pressed {{
            background: {self.brand_colors['accent']};
        }}
        QTableWidget {{
            border: 1px solid #d0d5e0;
            border-radius: 5px;
            background: white;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 13px;
            gridline-color: #e6e6e6;
            alternate-background-color: #f9f9f9;
        }}
        QHeaderView::section {{
            background: {self.brand_colors['primary']};
            color: white;
            font-weight: bold;
            padding: 6px;
            border: none;
        }}
        QStatusBar {{
            background: {self.brand_colors['neutral_light']};
            color: {self.brand_colors['text']};
            border-top: 1px solid #d0d5e0;
        }}
        QToolTip {{
            background-color: {self.brand_colors['primary']};
            color: white;
            border: none;
            padding: 5px;
            opacity: 200;
        }}
        """

    def _init_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create premium header with gradient
        header = QLabel("Trade Simulator by Vijayshree")
        header.setAlignment(Qt.AlignCenter)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(self.brand_colors['primary']))
        gradient.setColorAt(1, QColor(self.brand_colors['secondary']))
        
        header.setStyleSheet(f"""
            color: white;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            padding: 20px;
            border-radius: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                      stop:0 {self.brand_colors['primary']}, 
                                      stop:1 {self.brand_colors['secondary']});
        """)
        main_layout.addWidget(header)
        
        # Main content in a horizontal layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        main_layout.addLayout(content_layout)
        
        # Left panel (inputs)
        input_panel = self._create_input_panel()
        content_layout.addWidget(input_panel)
        
        # Right panel (outputs + orderbook)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Outputs panel
        output_panel = self._create_output_panel()
        right_layout.addWidget(output_panel)
        
        # Orderbook panel
        orderbook_panel = self._create_orderbook_panel()
        right_layout.addWidget(orderbook_panel)
        
        content_layout.addWidget(right_panel)
        
        # Set content layout stretch factors (40/60)
        content_layout.setStretchFactor(input_panel, 4)
        content_layout.setStretchFactor(right_panel, 6)
        
        # Status bar with connection indicator
        status_bar = self.statusBar()
        self.status_label = QLabel("● Disconnected")
        self.status_label.setStyleSheet(f"color: {self.brand_colors['danger']}; font-weight: bold; padding: 3px;")
        status_bar.addPermanentWidget(self.status_label)
        
        # Version info on the left
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet(f"color: {self.brand_colors['primary']}; font-style: italic;")
        status_bar.addWidget(version_label)
        
        # Update timer at 2 seconds interval
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_outputs)
        self.update_timer.start(2000)
        
        # Register callback
        self.ws_client.register_callback(self._handle_orderbook_update)

    def _create_input_panel(self):
        panel = QGroupBox("Input Parameters")
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 25, 15, 15)
        
        # Exchange selection
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["OKX", "Binance", "Coinbase", "Kraken"])
        self.exchange_combo.setToolTip("Select the exchange to simulate")
        layout.addRow("Exchange:", self.exchange_combo)
        
        # Asset selection
        self.asset_combo = QComboBox()
        self.asset_combo.addItems(["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "XRP-USDT-SWAP"])
        self.asset_combo.setToolTip("Select the trading pair")
        layout.addRow("Asset:", self.asset_combo)
        
        # Order type
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit", "Stop", "Take Profit"])
        self.order_type_combo.setToolTip("Select the order type")
        layout.addRow("Order Type:", self.order_type_combo)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 10000.0)
        self.quantity_spin.setValue(100.0)
        self.quantity_spin.setSingleStep(10.0)
        self.quantity_spin.setSuffix(" USD")
        self.quantity_spin.setToolTip("Enter the order size in USD")
        layout.addRow("Quantity:", self.quantity_spin)
        
        # Volatility
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setRange(0.0, 1.0)
        self.volatility_spin.setValue(0.02)
        self.volatility_spin.setSingleStep(0.01)
        self.volatility_spin.setToolTip("Set the market volatility (0-1)")
        layout.addRow("Volatility:", self.volatility_spin)
        
        # Fee tier
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["Tier 1 (VIP)", "Tier 2 (Pro)", "Tier 3 (Standard)"])
        self.fee_tier_combo.setToolTip("Select your fee tier")
        layout.addRow("Fee Tier:", self.fee_tier_combo)
        
        # Add some space
        layout.addRow("", QLabel(""))
        
        # Simulate button
        simulate_button = QPushButton("Simulate Trade")
        simulate_button.setToolTip("Run the simulation with current parameters")
        simulate_button.clicked.connect(self._update_outputs)
        layout.addRow("", simulate_button)
        
        panel.setLayout(layout)
        return panel

    def _create_output_panel(self):
        panel = QGroupBox("Simulation Results")
        layout = QFormLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 25, 15, 15)
        
        # Create styled output labels
        label_style = f"""
            background: {self.brand_colors['neutral_light']};
            border: 1px solid #d0d5e0;
            border-radius: 4px;
            padding: 6px;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-weight: bold;
        """
        
        self.slippage_label = QLabel("0.00%")
        self.slippage_label.setStyleSheet(label_style)
        self.slippage_label.setToolTip("Estimated price slippage based on order size and market depth")
        layout.addRow("Expected Slippage:", self.slippage_label)
        
        self.fees_label = QLabel("0.00 USD")
        self.fees_label.setStyleSheet(label_style)
        self.fees_label.setToolTip("Trading fees based on selected fee tier")
        layout.addRow("Expected Fees:", self.fees_label)
        
        self.impact_label = QLabel("0.00%")
        self.impact_label.setStyleSheet(label_style)
        self.impact_label.setToolTip("Estimated market impact of your order")
        layout.addRow("Market Impact:", self.impact_label)
        
        self.net_cost_label = QLabel("0.00 USD")
        self.net_cost_label.setStyleSheet(f"{label_style} color: {self.brand_colors['primary']};")
        self.net_cost_label.setToolTip("Total cost including slippage, impact and fees")
        layout.addRow("Net Cost:", self.net_cost_label)
        
        self.maker_taker_label = QLabel("50/50")
        self.maker_taker_label.setStyleSheet(label_style)
        self.maker_taker_label.setToolTip("Estimated maker/taker ratio")
        layout.addRow("Maker/Taker:", self.maker_taker_label)
        
        self.latency_label = QLabel("0 ms")
        self.latency_label.setStyleSheet(label_style)
        self.latency_label.setToolTip("Internal processing latency")
        layout.addRow("Internal Latency:", self.latency_label)
        
        self.last_update_label = QLabel("-")
        self.last_update_label.setStyleSheet(label_style)
        self.last_update_label.setToolTip("Time of last data update")
        layout.addRow("Last Update:", self.last_update_label)
        
        panel.setLayout(layout)
        return panel

    def _create_orderbook_panel(self):
        panel = QGroupBox("Live Orderbook")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 25, 15, 15)
        
        # Better labels for the orderbook columns
        headers = ["Price (Bid) | Size", "Price (Ask) | Size"]
        
        # Create a styled orderbook table with more rows
        self.orderbook_table = QTableWidget(7, 2)  # Increased to 7 rows
        self.orderbook_table.setHorizontalHeaderLabels(headers)
        self.orderbook_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orderbook_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orderbook_table.setAlternatingRowColors(True)
        self.orderbook_table.setToolTip("Live market orderbook data")
        
        # Make the orderbook easier to read
        self.orderbook_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: 14px;
                border: 1px solid #d0d5e0;
                border-radius: 5px;
                background: white;
                gridline-color: #e6e6e6;
                alternate-background-color: #f5f7fa;
            }}
            QHeaderView::section {{
                background: {self.brand_colors['primary']};
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid #f0f0f0;
            }}
        """)
        
        # Set minimum height for the orderbook to ensure it's visible
        self.orderbook_table.setMinimumHeight(250)
        layout.addWidget(self.orderbook_table)
        
        # Last updated label with styling
        self.refresh_label = QLabel("Last updated: -")
        self.refresh_label.setAlignment(Qt.AlignRight)
        self.refresh_label.setStyleSheet(f"color: {self.brand_colors['primary']}; font-style: italic;")
        layout.addWidget(self.refresh_label)
        
        panel.setLayout(layout)
        return panel

    async def _handle_orderbook_update(self, orderbook_data):
        """Handler for orderbook updates"""
        if self._update_in_progress:
            return
        
        try:
            self._update_in_progress = True
            
            # Store orderbook data
            self.current_orderbook = orderbook_data
            
            # Update connection status
            self.connected = True
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet(f"color: {self.brand_colors['success']}; font-weight: bold; padding: 3px;")
            
            # Update the table with orderbook data
            try:
                bids = orderbook_data.get('bids', [])[:7]  # Get up to 7 bids
                asks = orderbook_data.get('asks', [])[:7]  # Get up to 7 asks
                
                # Clear the table first
                self.orderbook_table.clearContents()
                
                # Update table with better formatting
                for i in range(min(7, self.orderbook_table.rowCount())):
                    # Set bid data (if available)
                    if i < len(bids):
                        try:
                            price = float(bids[i][0])
                            size = float(bids[i][1])
                            
                            # Format with a clear separator between price and size
                            bid_str = f"{price:.2f} | {size:.4f}"
                            bid_item = QTableWidgetItem(bid_str)
                            bid_item.setTextAlignment(Qt.AlignCenter)  # Center align text
                            bid_item.setForeground(QColor(self.brand_colors['bid']))
                            self.orderbook_table.setItem(i, 0, bid_item)
                        except (ValueError, IndexError) as e:
                            self.logger.warning(f"Error formatting bid: {e}")
                    
                    # Set ask data (if available)
                    if i < len(asks):
                        try:
                            price = float(asks[i][0])
                            size = float(asks[i][1])
                            
                            # Format with a clear separator between price and size
                            ask_str = f"{price:.2f} | {size:.4f}"
                            ask_item = QTableWidgetItem(ask_str)
                            ask_item.setTextAlignment(Qt.AlignCenter)  # Center align text
                            ask_item.setForeground(QColor(self.brand_colors['ask']))
                            self.orderbook_table.setItem(i, 1, ask_item)
                        except (ValueError, IndexError) as e:
                            self.logger.warning(f"Error formatting ask: {e}")
                
                # Calculate and show spread
                if asks and bids:
                    try:
                        best_ask = float(asks[0][0])
                        best_bid = float(bids[0][0])
                        spread = best_ask - best_bid
                        spread_pct = (spread / best_bid) * 100
                        
                        # Update the label with spread information
                        self.refresh_label.setText(
                            f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')} | " +
                            f"Spread: {spread:.2f} ({spread_pct:.2f}%)"
                        )
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"Error calculating spread: {e}")
                        self.refresh_label.setText(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
                else:
                    self.refresh_label.setText(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
                
            except Exception as e:
                self.logger.error(f"Error updating orderbook: {e}")
                self.refresh_label.setText(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Update timestamp
            self.last_update_time = datetime.datetime.now()
            
            # Update outputs
            self._update_outputs()
            
        except Exception as e:
            self.logger.error(f"Error in orderbook update: {e}")
        finally:
            self._update_in_progress = False

    def _update_outputs(self):
        """Update simulation outputs based on current data"""
        if not self.current_orderbook or self._update_in_progress:
            return
        
        try:
            # Get input values
            order_size = self.quantity_spin.value()
            volatility = self.volatility_spin.value()
            
            # Try to extract data
            try:
                asks = self.current_orderbook.get('asks', [])
                bids = self.current_orderbook.get('bids', [])
                
                if asks and bids:
                    # Calculate basic values
                    best_ask = float(asks[0][0])
                    best_bid = float(bids[0][0])
                    spread = best_ask - best_bid
                    
                    # Calculate market depth
                    market_depth = sum(float(size) for _, size in asks[:5]) + \
                                  sum(float(size) for _, size in bids[:5])
                    
                    # Calculate slippage
                    slippage = self.slippage_model.estimate_slippage(
                        order_size=order_size,
                        market_depth=market_depth,
                        volatility=volatility,
                        timestamp=self.current_orderbook.get('timestamp', 0)
                    )
                    self._update_value_with_color(self.slippage_label, f"{slippage:.2%}", slippage, 0.01, 0.03)
                    
                    # Calculate fees
                    fee_tier = self.fee_tier_combo.currentText()
                    fee_rate = 0.001 if "VIP" in fee_tier else 0.0008 if "Pro" in fee_tier else 0.0006
                    fees = order_size * fee_rate
                    self.fees_label.setText(f"{fees:.2f} USD")
                    
                    # Calculate impact
                    impact = self.market_impact_model.estimate_market_impact(
                        order_quantity=order_size,
                        market_depth=market_depth,
                        time_horizon=1.0
                    )
                    self._update_value_with_color(self.impact_label, f"{impact:.2%}", impact, 0.01, 0.03)
                    
                    # Calculate total cost
                    net_cost = order_size * (1 + slippage + impact) + fees
                    self.net_cost_label.setText(f"{net_cost:.2f} USD")
                    
                    # Estimate maker/taker ratio
                    maker_prob = self.maker_taker_model.predict_maker_probability(
                        order_size=order_size,
                        market_depth=market_depth,
                        spread=spread,
                        timestamp=self.current_orderbook.get('timestamp', 0),
                        volatility=volatility
                    )
                    maker_pct = maker_prob * 100
                    taker_pct = (1 - maker_prob) * 100
                    self.maker_taker_label.setText(f"{maker_pct:.0f}/{taker_pct:.0f}")
                    
                    # Update latency and timestamp
                    import time
                    if self.last_update_time:
                        elapsed = (time.time() - self.last_update_time.timestamp()) * 1000
                        self.latency_label.setText(f"{elapsed:.1f} ms")
                        self.last_update_label.setText(self.last_update_time.strftime("%H:%M:%S"))
                
            except Exception as e:
                self.logger.warning(f"Error calculating outputs: {e}")
                
        except Exception as e:
            self.logger.error(f"Error updating outputs: {e}")
            
    def _update_value_with_color(self, label, text, value, warn_threshold, danger_threshold):
        """Update a label with color-coded value based on thresholds"""
        label.setText(text)
        
        base_style = f"""
            background: {self.brand_colors['neutral_light']};
            border: 1px solid #d0d5e0;
            border-radius: 4px;
            padding: 6px;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-weight: bold;
        """
        
        if value < warn_threshold:
            label.setStyleSheet(f"{base_style} color: {self.brand_colors['success']};")
        elif value < danger_threshold:
            label.setStyleSheet(f"{base_style} color: {self.brand_colors['warning']};")
        else:
            label.setStyleSheet(f"{base_style} color: {self.brand_colors['danger']};") 