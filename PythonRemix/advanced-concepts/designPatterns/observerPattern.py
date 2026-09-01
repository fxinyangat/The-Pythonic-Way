"""
The Observer Pattern is a behavioral design pattern that defines a one-to-many
dependency between objects. When one object (the Subject) changes its state, 
all of its dependents (Observers) are notified and updated automatically.
It is the foundation of event-driven programming, often referred to as the 
Publish-Subscribe model.

Core Components
*   Subject (Publisher): Holds the primary state and maintains a list of observers. 
It provides methods to attach, detach, and notify observers.
*   Observer (Subscriber): Defines an updating interface for objects that should be notified of changes in a subject.
*   Concrete Subject / Concrete Observer: The actual implementations containing specific application logic.


When to Use ItState Dependency: 
*   When a change to one object requires changing others, and you don’t know how many objects need to change.
*   Decoupled Communication: When an object should be able to notify other objects without making assumptions about who or what those objects are.
*   UI Updates: In graphical user interfaces where structural models (data) must update views (visual panels) automatically upon changing values.
"""

from abc import ABC, abstractmethod

# 1. Observer Interface
class Subscriber(ABC):
    @abstractmethod
    def update(self, headline: str) -> None:
        pass

# 2. Subject Interface
class NewsAgency(ABC):
    def __init__(self):
        self._subscribers: list[Subscriber] = []

    def attach(self, subscriber: Subscriber) -> None:
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def detach(self, subscriber: Subscriber) -> None:
        self._subscribers.remove(subscriber)

    def notify(self, headline: str) -> None:
        for subscriber in self._subscribers:
            subscriber.update(headline)

# 3. Concrete Subject
class TechNewsAgency(NewsAgency):
    def __init__(self):
        super().__init__()
        self._latest_headline = ""

    def publish_breaking_news(self, headline: str) -> None:
        self._latest_headline = headline
        print(f"\n[Agency] Breaking News Published: {headline}")
        # Broadcast the change to all observers automatically
        self.notify(headline)

# 4. Concrete Observers
class EmailSubscriber(Subscriber):
    def __init__(self, email: str):
        self.email = email

    def update(self, headline: str) -> None:
        print(f"  -> Email sent to {self.email}: '{headline}'")

class SMSSubscriber(Subscriber):
    def __init__(self, phone: str):
        self.phone = phone

    def update(self, headline: str) -> None:
        print(f"  -> SMS sent to {self.phone}: '{headline}'")

# Execution
if __name__ == "__main__":
    agency = TechNewsAgency()

    # Create clients
    user1 = EmailSubscriber("alice@example.com")
    user2 = SMSSubscriber("+1-555-0199")

    # Hook up the connections
    agency.attach(user1)
    agency.attach(user2)

    # Publish news - triggers notifications automatically
    agency.publish_breaking_news("Python 4.0 Released!")
    
    # Unsubscribe a client
    agency.detach(user1)
    
    # Next update only goes to remaining subscribers
    agency.publish_breaking_news("AI Models Learn to Type Faster!")


# Advanced: Using Callables as Observers


