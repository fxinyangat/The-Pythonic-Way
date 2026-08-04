# MROS
# Mixins are small classes that add one focused capability, 
# designed to be mixed into a hierarchy via multiple inheritance.
# MRO makes this safe.

class BaseAccount:
    def __init__(self, owner:str, balance:float):
        self.owner = owner
        self.balance = balance
        
    def deposit(self, amount:float):
        if not isinstance(amount,float) or amount < 0:
            return ValueError("Amount is not Valid")
        
        self.balance += amount
        return self.balance
    
class AuditMixin:
    """Logs every deposit to an audit trail"""
    
    def deposit(self, amount:float):
        print(f"[AUDIT] {self.owner} depositing ${amount:.2f}")
        result = super().deposit(amount)
        
        print(f"[Audit] new balance ${self.balance:.2f}")
        
        return result
    
class FraudMixin:
    THRESHILD = 10_000
    
    def deposit(self,amount:float):
        if amount > self.THRESHILD:
            print(f"[FRAUD ALERT] Large Deposit ${amount:.2f} - flagged for review")
        return super().deposit(amount) # hands of to the next MRO
    
class PremiumAccount(AuditMixin, FraudMixin, BaseAccount):
    pass



print(PremiumAccount.mro())         


# Practical rules to internalize
# Always call super() in every class that participates in multiple inheritance
# — if you skip it in one class, you silently break the chain for everything 
# below it in the MRO.
# Put more specific (leaf) classes before less specific (base) classes in your 
# class Foo(More, Less) declaration — this matches what C3 expects and avoids TypeError.
# Use ClassName.__mro__ whenever a method lookup behaves unexpectedly. 
# The MRO tuple tells you exactly what Python will search and in what order 
# — it removes all the guesswork.
# Mixins should never call __init__ with fixed arguments or hardcode which 
# 
# parent they hand off to. They should use super() unconditionally and rely on 
# MRO to route correctly.
    
    


            
        