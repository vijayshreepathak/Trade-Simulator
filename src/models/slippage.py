import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple, Dict
import logging
from datetime import datetime

class SlippageModel:
    def __init__(self):
        """Initialize the slippage estimation model."""
        self.model = LinearRegression()
        self.feature_names = ['order_size', 'market_depth', 'volatility', 'time_of_day']
        self.logger = logging.getLogger(__name__)
        self.historical_data = []
        self.is_trained = False

    def prepare_features(self, 
                        order_size: float,
                        market_depth: float,
                        volatility: float,
                        timestamp: datetime) -> np.ndarray:
        """
        Prepare features for the model.
        
        Args:
            order_size: Size of the order
            market_depth: Available market depth
            volatility: Market volatility
            timestamp: Current timestamp
            
        Returns:
            Array of features
        """
        # Convert time of day to a continuous feature (0-1)
        time_of_day = (timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second) / (24 * 3600)
        
        # Normalize features
        normalized_size = order_size / market_depth
        normalized_depth = np.log1p(market_depth)
        
        return np.array([[normalized_size, normalized_depth, volatility, time_of_day]])

    def update_model(self, 
                    order_size: float,
                    market_depth: float,
                    volatility: float,
                    timestamp: datetime,
                    actual_slippage: float):
        """
        Update the model with new data point.
        
        Args:
            order_size: Size of the order
            market_depth: Available market depth
            volatility: Market volatility
            timestamp: Current timestamp
            actual_slippage: Observed slippage
        """
        try:
            features = self.prepare_features(order_size, market_depth, volatility, timestamp)
            
            # Store historical data
            self.historical_data.append({
                'features': features[0],
                'slippage': actual_slippage,
                'timestamp': timestamp
            })
            
            # Retrain model if we have enough data
            if len(self.historical_data) >= 10:
                self._retrain_model()
                
        except Exception as e:
            self.logger.error(f"Error updating model: {e}")
            raise

    def _retrain_model(self):
        """Retrain the model using historical data."""
        try:
            if len(self.historical_data) < 10:
                return
                
            # Prepare training data
            X = np.array([data['features'] for data in self.historical_data])
            y = np.array([data['slippage'] for data in self.historical_data])
            
            # Train model
            self.model.fit(X, y)
            self.is_trained = True
            
            # Remove old data points if we have too many
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error retraining model: {e}")
            raise

    def estimate_slippage(self,
                         order_size: float,
                         market_depth: float,
                         volatility: float,
                         timestamp: datetime) -> float:
        """
        Estimate slippage for a given order.
        
        Args:
            order_size: Size of the order
            market_depth: Available market depth
            volatility: Market volatility
            timestamp: Current timestamp
            
        Returns:
            Estimated slippage as a percentage
        """
        try:
            if not self.is_trained:
                # Return a simple estimate if model is not trained
                return (order_size / market_depth) * volatility
                
            features = self.prepare_features(order_size, market_depth, volatility, timestamp)
            estimated_slippage = self.model.predict(features)[0]
            
            # Ensure non-negative slippage
            return max(0.0, float(estimated_slippage))
            
        except Exception as e:
            self.logger.error(f"Error estimating slippage: {e}")
            # Return a simple estimate in case of error
            return (order_size / market_depth) * volatility

    def get_model_metrics(self) -> Dict:
        """
        Get model performance metrics.
        
        Returns:
            Dictionary containing model metrics
        """
        if not self.is_trained:
            return {
                'is_trained': False,
                'data_points': len(self.historical_data)
            }
            
        try:
            X = np.array([data['features'] for data in self.historical_data])
            y = np.array([data['slippage'] for data in self.historical_data])
            
            return {
                'is_trained': True,
                'data_points': len(self.historical_data),
                'r2_score': self.model.score(X, y),
                'coefficients': dict(zip(self.feature_names, self.model.coef_)),
                'intercept': float(self.model.intercept_)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating model metrics: {e}")
            return {
                'is_trained': True,
                'data_points': len(self.historical_data),
                'error': str(e)
            } 