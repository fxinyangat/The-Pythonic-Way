"""
The Chain of Responsibility Pattern is a behavioral design pattern that lets
you pass requests along a chain of handlers. Upon receiving a request, 
each handler decides either to process the request or to pass it to the next 
handler in the chain.This pattern decouples the sender of a request from its 
receivers, giving multiple objects a chance to handle the request.

Core Components
*   Handler: Defines an interface for handling requests and optionally implements the successor link.
*   Base Handler: An optional boilerplate class that stores a reference to the next handler and manages passing requests down the line.
*   Concrete Handlers: Actual processing units that handle specific requests or pass them forward.
*   Client: Configures the chain sequence and submits the initial request to the first handler.

"""
from abc import ABC, abstractmethod
from typing import Optional

# 1. The Handler Interface
class SupportHandler(ABC):
    @abstractmethod
    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        pass

    @abstractmethod
    def handle(self, request_type: str, severity: int) -> Optional[str]:
        pass

# 2. Base Handler (Manages the chaining logic)
class BaseSupportHandler(SupportHandler):
    _next_handler: Optional[SupportHandler] = None

    def set_next(self, handler: SupportHandler) -> SupportHandler:
        self._next_handler = handler
        # Returning the handler allows convenient linking like h1.set_next(h2).set_next(h3)
        return handler

    def handle(self, request_type: str, severity: int) -> Optional[str]:
        if self._next_handler:
            return self._next_handler.handle(request_type, severity)
        return None

# 3. Concrete Handlers
class FrontDeskHandler(BaseSupportHandler):
    def handle(self, request_type: str, severity: int) -> Optional[str]:
        if request_type == "subscription" or severity <= 2:
            return f"Front Desk: Resolved simple request ('{request_type}')."
        print("Front Desk: Too complex. Passing to Tech Lead...")
        return super().handle(request_type, severity)

class TechLeadHandler(BaseSupportHandler):
    def handle(self, request_type: str, severity: int) -> Optional[str]:
        if request_type == "bug_fix" and severity <= 5:
            return f"Tech Lead: Patched software glitch ('{request_type}')."
        print("Tech Lead: Requires management authorization. Passing to Director...")
        return super().handle(request_type, severity)

class DirectorHandler(BaseSupportHandler):
    def handle(self, request_type: str, severity: int) -> Optional[str]:
        if severity <= 10:
            return f"Director: Authorized high-priority infrastructure emergency."
        return "Chain Exhausted: Request could not be handled."

# Execution
if __name__ == "__main__":
    # Setup individuals
    front_desk = FrontDeskHandler()
    tech_lead = TechLeadHandler()
    director = DirectorHandler()

    # Build the sequential chain: Front Desk -> Tech Lead -> Director
    front_desk.set_next(tech_lead).set_next(director)

    # Issue tickets to the front of the chain
    print("\n--- Ticket 1 ---")
    print(front_desk.handle("subscription", severity=1))

    print("\n--- Ticket 2 ---")
    print(front_desk.handle("bug_fix", severity=4))

    print("\n--- Ticket 3 ---")
    print(front_desk.handle("db_crash", severity=9))
