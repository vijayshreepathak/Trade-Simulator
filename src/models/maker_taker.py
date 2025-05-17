import numpy as np
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import random

class MakerTakerModel:
    def __init__(self):
        """Initialize the maker/taker proportion prediction model."""
        self.model = LogisticRegression(random_state=42)
        self.feature_names = [
            'order_size',
            'market_depth',
            'spread',
            'time_of_day',
            'volatility'
        ]
        self.logger = logging.getLogger(__name__)
        self.historical_data = []
        self.is_trained = False
        self.last_prediction = 0.5  # Default to 50/50 split

    def prepare_features(self,
                        order_size: float,
                        market_depth: float,
                        spread: float,
                        timestamp: datetime,
                        volatility: float) -> np.ndarray:
        """
        Prepare features for the model.
        
        Args:
            order_size: Size of the order
            market_depth: Available market depth
            spread: Current bid-ask spread
            timestamp: Current timestamp
            volatility: Market volatility
            
        Returns:
            Array of features
        """
        # Convert time of day to a continuous feature (0-1)
        time_of_day = (timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second) / (24 * 3600)
        
        # Normalize features
        normalized_size = order_size / market_depth
        normalized_depth = np.log1p(market_depth)
        normalized_spread = spread / market_depth
        
        return np.array([[
            normalized_size,
            normalized_depth,
            normalized_spread,
            time_of_day,
            volatility
        ]])

    def update_model(self, order_size: float, market_depth: float, spread: float,
                    timestamp: datetime, volatility: float, is_maker: bool = None):
        try:
            # Generate features
            features = self.prepare_features(order_size, market_depth, spread, timestamp, volatility)
            
            # If is_maker is None, randomly assign it for training purposes
            if is_maker is None:
                is_maker = random.random() > 0.5
            
            # Store data
            self.historical_data.append({
                'features': features[0],
                'is_maker': is_maker,
                'timestamp': timestamp
            })
            
            # Retrain if we have enough data
            if len(self.historical_data) >= 10:
                self._retrain_model()
                
        except Exception as e:
            self.logger.error(f"Error updating model: {e}")
            # Don't raise the exception, just log it

    def _retrain_model(self):
        """Retrain the model using historical data."""
        try:
            if len(self.historical_data) < 10:
                return
                
            X = np.array([data['features'] for data in self.historical_data])
            y = np.array([data['is_maker'] for data in self.historical_data])
            
            # Only retrain if we have at least 2 classes
            if len(set(y)) < 2:
                # If we only have one class, use a simple heuristic
                self.last_prediction = 0.5 if y[0] else 0.5
                return
                
            self.model.fit(X, y)
            self.is_trained = True
            
            # Keep only the last 1000 samples
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error retraining model: {e}")
            # Don't raise the exception, just log it

    def predict_maker_probability(self, order_size: float, market_depth: float,
                                spread: float, timestamp: datetime, volatility: float) -> float:
        """
        Predict the probability of an order being a maker order.
        
        Args:
            order_size: Size of the order
            market_depth: Available market depth
            spread: Current bid-ask spread
            timestamp: Current timestamp
            volatility: Market volatility
            
        Returns:
            Probability of the order being a maker order (0-1)
        """
        try:
            if not self.is_trained:
                return self.last_prediction
                
            features = self.prepare_features(order_size, market_depth, spread, timestamp, volatility)
            prob = self.model.predict_proba([features])[0][1]
            self.last_prediction = prob
            return prob
            
        except Exception as e:
            self.logger.error(f"Error predicting maker probability: {e}")
            return self.last_prediction  # Return last known prediction on error

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
            y = np.array([data['is_maker'] for data in self.historical_data])
            
            return {
                'is_trained': True,
                'data_points': len(self.historical_data),
                'accuracy': self.model.score(X, y),
                'coefficients': dict(zip(self.feature_names, self.model.coef_[0])),
                'intercept': float(self.model.intercept_[0])
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating model metrics: {e}")
            return {
                'is_trained': True,
                'data_points': len(self.historical_data),
                'error': str(e)
            } 