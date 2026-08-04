# Create code to manage fintech accounts: create, close, deposit, see balance

from abc import ABC, abstractmethod
import random

class Account(ABC):
    def __init__(self, owner:str, balance:float=0.0):
        self._owner = owner
        self._balance = balance
        self._account_number = None
        self._acc_status = False
        self._post_init()

    def _post_init(self):
        self._account_number = self._generate_acc_number()
        print(f"Acc Number is: {self._account_number}")

    # def _generate_acc_number():
    #     return random.randint(10**9, 10**10 - 1)
    
    def ensure_active(func):
        def wrapper(self, *args, **kwargs):
            try:
                if self._acc_status: 
                    result = func(self, *args, **kwargs)
                    return result
                else:
                    print("Can't Process transaction - Account Closed!")
                    return "Account Inacctive"
            except Exception as e:
                print(f"Error occured: {e}")
                
            
        return wrapper
        
    @staticmethod
    def _generate_acc_number():
        return random.randint(10**9, 10**10 - 1)
        
    def _validate_amount(self, amount:float, action:str):
        if amount < 0:
            raise ValueError(f'Invalid Amount {amount}')
        if amount > self._balance and action == 'withdraw':
            raise ValueError('Insufficient balance')
          
    @property
    def account_details(self):
        owner = self._owner
        acc = self._account_number
        print(f"Account {acc} belongs to {owner}")
        return [{"owner": owner},
                {"acc_number": acc
                 }]
    
    @property
    def check_balance(self):
        bal = self._balance
        print(f"Account {self._account_number} has balance of {self._balance}")

        return bal
    
    
    @property
    def account_status(self):
        return 'Active' if self._acc_status else 'Inactive'
    
    @ensure_active
    def deposit_funds(self, amount: float):
        try:
            self._validate_amount( amount, 'deposit')
            
        except ValueError as e:
            print(f'Deposit Failed: {e}')
        except Exception as e2:
            print(f"Something else went wrong {e2}")
        
        else:
            self._balance += amount     
        
        finally:
            print("Deposit Operation Done")
            
        return f"Deposit succesful - New Balacne: {self.check_balance}"
    
    def withdraw_funds(self, amount:float):
        
        try:
            self._validate_amount(amount, 'withdraw')
            
        except ValueError as e:
            print(f'Withdraw Failed: {e}')
        except Exception as e2:
            print(f"Something else went wrong {e2}")
        
        else:
            self._balance -= amount     
        
        finally:
            print("withdraw Operation Done")
            
        return f"Withdraw succefull - New Balacne: {self.check_balance}"
        
    
    @abstractmethod
    def createAccount(self):
        pass
    
    def manage_account(self, operation:str = 'close'):
        if self._acc_status and operation == 'close':
            self._acc_status = False
            return (f"Account {self.account_details[1]['acc_number']} has been closed")
        elif not self._acc_status and operation == 'open':
            self._acc_status = True
            return (f"Account {self.account_details[1]['acc_number']} has been opened")
        else:
            return (f"Account Already Open/Closed")
       
            
    
    def __str__(self):
        
        
        print(f"Status: {self.account_status}\n Balance: {self.check_balance}")
        return (f"Status: {self.account_status}\n Balance: {self.check_balance}")
  
    
    
    
    


