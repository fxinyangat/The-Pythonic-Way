"""
The Adapter pattern is a structural design pattern that allows incompartible interfaces
to collaborate by acting as a translator btn them. It wraps the existing class
(adaptee) with a new interface (the adapter) to match the specs that your client code 
expects, eliminating the need t o modify the legacy code or third party APIs

CORE Components
*   Client: The code containing your primary business logic that relies on a specific interface.
*   Target Interface: The standardized structure or interface that the Client expects to use.
*   Adaptee: The useful legacy class or third-party library with an incompatible interface.
*   Adapter: A middleman class implementing the Target interface while passing calls to the Adaptee

When to Use ItLegacy Migrations: 
-   When wrapping old systems to match modern application architectures.
-   Third-Party Code: When working with external vendor APIs whose interfaces don't align with your codebase.
-   Data Normalization: When a stable client expects a specific data object format, but various backends return different structures.
"""

from abc import ABC, abstractmethod

# 1. Target interface (what our client expects)

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount:float)->None:
        pass
    
#2. Adaptee (Legacy clss with incompartible interface)
class LegacyBankService:
    def make_wire_tranfer(self, amount_in_cents:int) -> None:
        print(f"Processing legacy wire transfer of {amount_in_cents} cents")
        
#3. Adapter (Bridegs the target interface with legacy service)
class BankAdapter(PaymentProcessor):
    def __init__(self, legacy_service: LegacyBankService):
        self.legacy_service = legacy_service
        
    def pay(self, amount:float) -> None:
        amount_in_cents = int(amount*100)
        self.legacy_service.make_wire_tranfer(amount_in_cents)
        
#4 . Client code
def complete_checkout(processor: PaymentProcessor, checkout_total: float):
    processor.pay(checkout_total)
    
    
# Executiom

if __name__ == "__main__":
    legacy_bank = LegacyBankService()
    
    # wrap the incompartible object inside adapter
    
    adapted_processor = BankAdapter(legacy_bank)
    
    # run client
    
    complete_checkout(adapted_processor, 49.99)
        