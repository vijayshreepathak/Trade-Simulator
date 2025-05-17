import pytest
import numpy as np
from src.models.market_impact import AlmgrenChrissModel
from datetime import datetime

def test_market_impact_initialization():
    """Test model initialization with default parameters."""
    model = AlmgrenChrissModel()
    
    assert model.risk_aversion == 0.1
    assert model.volatility == 0.02
    assert model.temporary_impact == 0.1
    assert model.permanent_impact == 0.05

def test_market_impact_calculation():
    """Test market impact calculation."""
    model = AlmgrenChrissModel(
        risk_aversion=0.1,
        volatility=0.02,
        temporary_impact=0.1,
        permanent_impact=0.05
    )
    
    # Test with reasonable market parameters
    order_quantity = 1.0  # 1 BTC
    market_depth = 100.0  # 100 BTC
    time_horizon = 1.0    # 1 second
    
    impact = model.estimate_market_impact(
        order_quantity=order_quantity,
        market_depth=market_depth,
        time_horizon=time_horizon
    )
    
    # Verify impact is positive and reasonable
    assert impact > 0
    assert impact < 1.0  # Should be less than 100%

def test_optimal_execution():
    """Test optimal execution trajectory calculation."""
    model = AlmgrenChrissModel()
    
    total_quantity = 10.0  # 10 BTC
    time_horizon = 3600.0  # 1 hour
    initial_price = 50000.0  # $50,000
    num_steps = 100
    
    trajectory, prices = model.calculate_optimal_execution(
        total_quantity=total_quantity,
        time_horizon=time_horizon,
        initial_price=initial_price,
        num_steps=num_steps
    )
    
    # Verify trajectory properties
    assert len(trajectory) == num_steps
    assert len(prices) == num_steps
    
    # Verify trajectory starts at total quantity and ends at 0
    assert abs(trajectory[0] - total_quantity) < 1e-10
    assert abs(trajectory[-1]) < 1e-10
    
    # Verify trajectory is monotonically decreasing
    assert all(trajectory[i] >= trajectory[i+1] for i in range(len(trajectory)-1))
    
    # Verify prices are reasonable
    assert all(price > 0 for price in prices)
    assert all(abs(price - initial_price) < initial_price for price in prices)

def test_parameter_updates():
    """Test model parameter updates."""
    model = AlmgrenChrissModel()
    
    # Update parameters
    model.update_parameters(
        risk_aversion=0.2,
        volatility=0.03,
        temporary_impact=0.15,
        permanent_impact=0.08
    )
    
    # Verify updates
    assert model.risk_aversion == 0.2
    assert model.volatility == 0.03
    assert model.temporary_impact == 0.15
    assert model.permanent_impact == 0.08

def test_edge_cases():
    """Test model behavior with edge cases."""
    model = AlmgrenChrissModel(
        risk_aversion=0.1,
        volatility=0.02,
        temporary_impact=0.1,
        permanent_impact=0.05
    )
    
    # Test with very small order
    small_impact = model.estimate_market_impact(
        order_quantity=0.001,
        market_depth=100.0,
        time_horizon=1.0
    )
    assert small_impact > 0
    assert small_impact < 0.01  # Should be very small
    
    # Test with very large order relative to market depth
    large_impact = model.estimate_market_impact(
        order_quantity=50.0,  # 50% of market depth
        market_depth=100.0,
        time_horizon=1.0
    )
    assert large_impact > 0
    assert large_impact < 1.0  # Should be less than 100%
    
    # Test with very short time horizon
    short_impact = model.estimate_market_impact(
        order_quantity=1.0,
        market_depth=100.0,
        time_horizon=0.001
    )
    assert short_impact > 0
    assert short_impact < 1.0 