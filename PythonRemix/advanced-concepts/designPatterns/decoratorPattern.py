"""
The decorator pattern is a structural design pattern that lets you dynamically
attach new behaviours to objects by placing them inside special wrapper objects.
It provides a flexible alternative to inheritance (subclassing) for extending fucntionality
without chanigng the existing code.
 
Core ComponentsComponent: 
*   The base interface or abstract class defining the methods that can be altered dynamically.
*   Concrete Component: The basic object implementing the Component interface that defines the core behavior.
*   Base Decorator: A class that implements the Component interface and wraps a reference to a Component object.
*   Concrete Decorator: Classes that extend the Base Decorator to add specific new features, actions, or state
"""

# Example: Consider a coffee shop application. Instead of creating endless subclasses
# like CoffeeWithMilk, CoffeeWithSugar, and CoffeeWithMilkAndSugar, 
# you wrap a basic coffee with separate decorators.

from abc import ABC, abstractmethod

# 1. Component (The standard interface)
class Beverage(ABC):
    
    @abstractmethod
    def get_cost(self)->float:
        pass
    
    @abstractmethod
    def get_description(self)->str:
        pass
    
# 2. Concrete Component (the base object)

class SimpleCoffee(Beverage):
    def get_cost(self) ->float:
        return 2.00
    
    def get_description(self) ->str:
        return "Simple Coffee"
    
# 3. Base Decorator (Wraps the component)
class BeverageDecorator(Beverage, ABC):
    def __init__(self, beverage: Beverage):
        self._beverage = beverage
        
    def get_cost(self)->float:
        return self._beverage.get_cost()
    
    def get_description(self)->str:
        return self._beverage.get_description()
    
#4. Concrete Decorators (Adds Specific Behaviours)

class MilkDecorator(BeverageDecorator):
    def get_cost(self):
        return super().get_cost() + 0.50
    
    def get_description(self):
        return super().get_description() + ", Milk"
    
class SugarDecorator(BeverageDecorator):
    def get_cost(self):
            return super().get_cost() + 0.25
        
    def get_description(self):
            return super().get_description() + ", Sugar"
        
# Execution

if __name__ == "__main__":
    
    # Order plain cofffee
    
    order = SimpleCoffee()
    
    # Add milk
    
    order = MilkDecorator(order)
    
    # add sugar
    
    order = SugarDecorator(order)
    
     # Final output
    print(f"Order: {order.get_description()}")
    print(f"Total Cost: ${order.get_cost():.2f}")
    
    
    
