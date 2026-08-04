"""Abstrct Base Class and Protocol
ABC - Any class. platying this role must implement this methods - Nominla typing
Protocol - if you have the right methods you qualify automatically



"""

from abc import ABC, abstractmethod

class BankAccount(ABC):
    @abstractmethod
    def deposit(self, amount:float) ->float:
        """Add funds must return a new _balance"""
        
    @abstractmethod
    def withdraw(self, amount:float) ->float:
        """Remove funds must return a new _balance"""
        
    @abstractmethod
    def get_balance(self, amount:float) ->float:
        pass
    
    # Concrete method
    def transfer_to(self, other: "BankAccount", amount:float):
        self.withdraw(amount)
        other.deposit(amount)
        
        print(f"Transfered ${amount:.2f}")
        
# Concrete sub-class

class SavingsAccount(BankAccount):
    def __init__(self, owner:str, _balance: float = 0):
        self.owner = owner
        self._balance = _balance
        
    
    def deposit(self, amount:float) ->float:
        #check valid amount and limits
        self._balance += amount
        return self._balance
        
            
   
    def withdraw(self, amount:float) ->float:
            if amount > self._balance:
                raise ValueError("Inssuficient funds")
            
            self._balance -= amount
            
            return self._balance
            
     
    def get_balance(self) ->float:
        return self._balance
    
    def __repr__(self):
        return f"Savings Account ({self.owner!r} ${self._balance})"
    

class CurrentAccount(BankAccount):
    def __init__(self, owner:str, overdraft_limit: float = 500.0):
        self.owner = owner
        self._balance = 0
        self._overdraft_limit = overdraft_limit
        
    
    def deposit(self, amount:float) ->float:
        #check valid amount and limits
        self._balance += amount
        return self._balance
        
            
   
    def withdraw(self, amount:float) ->float:
            if amount > self._balance + self._overdraft_limit:
                raise ValueError("Inssuficient funds")
            
            self._balance -= amount
            
            return self._balance
            
     
    def get_balance(self) ->float:
        return self._balance
    
    def __repr__(self):
        return f"Current Account ({self.owner!r} ${self._balance + self._overdraft_limit})"
        
savings = SavingsAccount("xavier", 5000)


current = CurrentAccount("Alice")

print(f"Xavier _Balance intially: {savings.get_balance()}")
print(f"Alice _Balance intially: {current.get_balance()}")

savings.transfer_to(current, 1000)

print(f"Xavier _Balance after: {savings.get_balance()}")
print(f"Alice _Balance After: {current.get_balance()}")


# PROTOCOL

from typing import Protocol, runtime_checkable

@runtime_checkable
class Transactable(Protocol):
    @abstractmethod
    def deposit(self, amount:float) ->float:
        """Add funds must return a new _balance"""
        
    @abstractmethod
    def withdraw(self, amount:float) ->float:
        """Remove funds must return a new _balance"""
        
    @abstractmethod
    def get_balance(self, amount:float) ->float:
        pass
    
    # # Concrete method
    # def transfer_to(self, other: "BankAccount", amount:float):
    #     self.withdraw(amount)
    #     other.deposit(amount)
        
    #     print(f"Transfered ${amount:.2f}")

class DogeCoin:
    """Completely unrelated class — no inheritance from anything."""
    def __init__(self, owner: str):
        self.owner = owner
        self._balance = 0.0

    def deposit(self, amount: float) -> float:
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        self._balance -= amount
        return self._balance

    def get_balance(self) -> float:
        return self._balance
    
def print_statement(account: Transactable) -> None:
    # Works with anything that satisfies Transactable
    print(f"Current balance: ${account.get_balance():.2f}")
    
wallet = DogeCoin("Inyangat")

wallet.deposit(1000)

print_statement(wallet)
print_statement(savings)


print(isinstance(wallet, Transactable))    # True
print(isinstance(savings, Transactable))   # True
print(isinstance("hello", Transactable))   # False

"""
ABC vs Protocol — when to use which
Use ABC when:

You control all the classes that will implement the interface (your own codebase)
You want to provide shared concrete methods alongside the abstract ones (transfer_to above)
You want TypeError at instantiation time if someone forgets to implement a method
You want isinstance checks to be meaningful and explicit

Use Protocol when:

You're writing a function or library that should work with classes you don't control (third-party, user-provided)
You want duck typing with static analysis — the caller doesn't need to import or inherit from your interface
You're defining what a function needs from its argument, not what a class is"""


    
            


        
        
        
        
        