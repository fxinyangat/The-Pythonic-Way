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
    def run_with_timer(self):
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
backup.run_with_timer()


        

"""Create Account with methods to create account, fund account, withdraw from account, and close account."""

from abc import ABC, abstractmethod
import random


class Account(ABC):
    def __init__(self, owner: str, balance: float = 0.0):
        self._owner = owner
        self._account_number = self._generate_account_number()
        self._balance = balance
        self._is_active = False

    @staticmethod
    def _generate_account_number() -> int:
        return random.randint(100_000_000, 999_999_999)

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def account_number(self) -> int:
        return self._account_number

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient funds.")
        self._balance -= amount

    def close_account(self) -> None:
        self._is_active = False

    @abstractmethod
    def create_account(self) -> None:
        pass

    def __str__(self) -> str:
        status = "active" if self._is_active else "inactive"
        return (
            f"Account(owner={self._owner}, number={self._account_number}, "
            f"balance={self._balance:.2f}, status={status})"
        )


class FlexipayAccount(Account):
    def create_account(self) -> None:
        self._is_active = True
        print(f"Created account {self._account_number} for customer {self._owner}")


# if __name__ == "__main__":
#     flexi = FlexipayAccount("Xavier Inyangat")
#     flexi.create_account()
#     flexi.deposit(150.0)
#     flexi.withdraw(25.0)
#     print(flexi)





