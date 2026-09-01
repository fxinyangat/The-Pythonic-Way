"""
The Strategy Patttern is a behavioural pattern that alows you to define
a family of interchangeable algorithms, encapsulate each one inside its own class
and switch between them at run time based on user choice or environmental conditions.

Instead of masive hardcoed conditional statements (if/elif/else), the client
delegates the execution of the algorithm to an injected strategy object.


Core Components
*   Context: The class that maintains a reference to a strategy object and executes its behavior without knowing its specific type.
*   Strategy Interface: A common interface or abstract class that all concrete strategies must implement.
*   Concrete Strategies: Individual classes implementing the specific algorithm variations (e.g., different sorting styles, data formats, or math operations).
"""

from abc import ABC, abstractmethod

#1. Strategy interface
class ShippingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, weight_lbs: float) -> float:
        raise NotImplementedError("Subclasses must implelement own cost calculation")
    

    
#2. Concrete Strategies (the interchangeable algorithms)

class FedExStrategy(ShippingStrategy):
    def calculate_cost(self, weight_lbs: float) -> float:
        return 5.00 + (weight_lbs * 0.75)

class UPSStrategy(ShippingStrategy):
    def calculate_cost(self, weight_lbs: float) -> float:
        return 4.50 + (weight_lbs * 0.85)

class PostalServiceStrategy(ShippingStrategy):
    def calculate_cost(self, weight_lbs: float) -> float:
        return 2.00 + (weight_lbs * 0.40)
    
# 3. Context (The class using the strategy)

class OrderShippingCalculator:
    def __init__(self, strategy:ShippingStrategy):
        self._strategy = strategy #inject the strategy dependency here
    
    
        
    def set_strategy(self, strategy: ShippingStrategy):
        self._strategy = strategy
        
    def calculate(self, weight_lbs:float) -> float:
        return self._strategy.calculate_cost(weight_lbs)
    
# Execution
if __name__ == "__main__":
    
    package_weight = 10.0
    calculator = OrderShippingCalculator(FedExStrategy())
    
    print(f"FedEx Cost: {calculator.calculate(package_weight)}")
    
    # Customer changes their mind to use Postal Service at runtime
    calculator.set_strategy(PostalServiceStrategy())
    print(f"USPS Cost: ${calculator.calculate(package_weight):.2f}")
    
    """
    Pythonic Optimization: 
    First-Class FunctionsBecause Python supports first-class functions,
    you often do not need to create formal abstract classes or separate 
    structures for simple strategies. You can pass regular Python functions 
    directly as your strategies.
    """
    
# Example of Concrete strategies as functions
from collections.abc import Callable

def fedex_cost(weight:float) -> float: return 5.0 + (weight * 0.75)

def ups_cost(weight:float)->float: return 4.50 + (weight * 0.85)

class MicroCalculator:
    def __init__(self, strategy_callable:Callable[[float], float]):
        self.strategy = strategy_callable
        
    def calculate(self, weight:float) -> float:
        return self.strategy(weight)
# usage

calc = MicroCalculator(fedex_cost)

print(f"Functional FedEx Cost: ${calc.calculate(10.0):.2f}")


        

    