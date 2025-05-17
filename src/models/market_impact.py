import numpy as np
from typing import List, Tuple
import logging

class AlmgrenChrissModel:
    def __init__(self, 
                 risk_aversion: float = 0.1,
                 volatility: float = 0.02,
                 temporary_impact: float = 0.1,
                 permanent_impact: float = 0.05):
        """
        Initialize the Almgren-Chriss model with parameters.
        
        Args:
            risk_aversion: Risk aversion parameter (η)
            volatility: Market volatility (σ)
            temporary_impact: Temporary market impact parameter (γ)
            permanent_impact: Permanent market impact parameter (η)
        """
        self.risk_aversion = risk_aversion
        self.volatility = volatility
        self.temporary_impact = temporary_impact
        self.permanent_impact = permanent_impact
        self.logger = logging.getLogger(__name__)

    def calculate_optimal_execution(self,
                                  total_quantity: float,
                                  time_horizon: float,
                                  initial_price: float,
                                  num_steps: int = 100) -> Tuple[List[float], List[float]]:
        """
        Calculate optimal execution trajectory using Almgren-Chriss model.
        
        Args:
            total_quantity: Total quantity to execute
            time_horizon: Total time horizon for execution
            initial_price: Initial market price
            num_steps: Number of time steps for discretization
            
        Returns:
            Tuple of (execution_trajectory, expected_prices)
        """
        try:
            # Time grid
            t = np.linspace(0, time_horizon, num_steps)
            dt = time_horizon / (num_steps - 1)
            
            # Model parameters
            kappa = np.sqrt(self.risk_aversion * self.volatility**2 / self.temporary_impact)
            
            # Calculate optimal trajectory
            execution_trajectory = total_quantity * np.sinh(kappa * (time_horizon - t)) / np.sinh(kappa * time_horizon)
            
            # Calculate expected prices
            expected_prices = initial_price + self.permanent_impact * (total_quantity - execution_trajectory)
            
            return execution_trajectory.tolist(), expected_prices.tolist()
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal execution: {e}")
            raise

    def estimate_market_impact(self,
                             order_quantity: float,
                             market_depth: float,
                             time_horizon: float) -> float:
        """
        Estimate total market impact for a given order.
        
        Args:
            order_quantity: Size of the order
            market_depth: Available liquidity in the market
            time_horizon: Expected execution time horizon
            
        Returns:
            Estimated total market impact as a percentage
        """
        try:
            # Calculate temporary impact
            temp_impact = self.temporary_impact * (order_quantity / market_depth)
            
            # Calculate permanent impact
            perm_impact = self.permanent_impact * (order_quantity / market_depth)
            
            # Calculate risk component
            risk_component = self.risk_aversion * self.volatility * np.sqrt(time_horizon)
            
            # Total impact
            total_impact = temp_impact + perm_impact + risk_component
            
            return float(total_impact)
            
        except Exception as e:
            self.logger.error(f"Error estimating market impact: {e}")
            raise

    def update_parameters(self,
                         risk_aversion: float = None,
                         volatility: float = None,
                         temporary_impact: float = None,
                         permanent_impact: float = None):
        """
        Update model parameters.
        
        Args:
            risk_aversion: New risk aversion parameter
            volatility: New volatility parameter
            temporary_impact: New temporary impact parameter
            permanent_impact: New permanent impact parameter
        """
        if risk_aversion is not None:
            self.risk_aversion = risk_aversion
        if volatility is not None:
            self.volatility = volatility
        if temporary_impact is not None:
            self.temporary_impact = temporary_impact
        if permanent_impact is not None:
            self.permanent_impact = permanent_impact 