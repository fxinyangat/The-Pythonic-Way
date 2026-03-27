## Abstract Class : A class that can not be instatiated on its own; Meant to be sublclassed.
# they can contain abstract methods, which are declared but have no implementation.
# Abstract Class benefits
# - Preventss instatiation of the class itself
# - Requires children to use inherited abstract methods

from abc import ABC, abstractmethod

class Vehicle(ABC):
    
    @abstractmethod
    def go(self):
        pass

    @abstractmethod
    def stop(self):
        pass

# children to inherit from Vehicle

class Car(Vehicle):
    def go(self):
        print("You drive the car")


    def stop(self):
        print("You stop the car")
    

class motorCycle(Vehicle):
    def go(self):
        print("You ride a motorcycle")

    
    # def stop(self):
    #     print("You stop the motorcycle")

# motocycle = motorCycle()

# motocycle.go()
# motocycle.stop()


# Property decorator allows us to define a method as an attribute.

class Rectangle:
    def __init__(self, width, height):
        self._width = width # protected attributes
        self._height = height

    @property
    def width(self):
        return f"{self._width:.1f}"
    
    @property
    def height(self):
        return f"{self._height:.1f}"

    @width.setter
    def width(self, new_width):
        if new_width > 0:
            self._width = new_width
        else:
            print("width must be greatter than 0")

    @height.setter
    def height(self, new_height):
        if new_height > 0:
            self._height = new_height
        else:
            print("Height must be greatter than 0")
        


rect = Rectangle(3,4)



rect.width = 5
rect.height = -5

print(rect._width)
print(rect._height)


# PRO MOVE : using a "normal" method in Base class to wrapp an "abstract" method

import time
from abc import ABC, abstractmethod

class Task(ABC):
    def run_with_timeer(self):
        """The wrapper logic lives in the base class"""

        start = time.time()

        result = self.execute() # calls the subclass version
        print(f"Task took {time.time() - start:.4f} seconds")

        return result
    
    @abstractmethod
    def execute(self):
        """Subclass only focus on the core logic"""
        pass


class Databackup(Task):
    def execute(self):
        print("Backing up data")
        time.sleep(2)

backup = Databackup()
backup.run_with_timeer()




