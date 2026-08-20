
"""
The Abstract Factory pattern is a creational design pattern that allows you to produce
families of related or dependent objects without specifiying their concrete
classes. It acts as a "factory of factories", grouping individual object factories
that share common theme together.

Core ComponentsAbstract Factory: 
*   Declares an interface for operations that create abstract product objects.
*   Concrete Factory: Implements the operations to manufacture specific concrete product variants.
*   Abstract Product: Declares an interface or base class for a type of product object.
*   Concrete Product: Defines a product object to be created by the corresponding concrete factory. 
*   Client: Uses only interfaces declared by Abstract Factory and Abstract Product classes



When to Use ItTheme Dependency: 
*   When your system needs to be independent of how its products are created, composed, and represented.
*   Product Families: When your system needs to be configured with one of multiple families of products that are explicitly designed to be used together (e.g., Windows vs. Linux vs. Mac UI components).
*   Encapsulation: When you want to provide a class library of products, exposing only their interfaces, not their implementations.
"""





from abc import ABC, abstractmethod

# ==========================================
# 1. Abstract Products
# ==========================================
class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str:
        pass


# ==========================================
# 2. Concrete Products (Windows Variant)
# ==========================================
class WindowsButton(Button):
    def render(self) -> str:
        return "Rendering a button in Windows style."

class WindowsCheckbox(Checkbox):
    def render(self) -> str:
        return "Rendering a checkbox in Windows style."


# ==========================================
# 3. Concrete Products (Mac Variant)
# ==========================================
class MacButton(Button):
    def render(self) -> str:
        return "Rendering a button in macOS style."

class MacCheckbox(Checkbox):
    def render(self) -> str:
        return "Rendering a checkbox in macOS style."


# ==========================================
# 4. Abstract Factory
# ==========================================
class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass


# ==========================================
# 5. Concrete Factories
# ==========================================
class WindowsFactory(UIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(UIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()


# ==========================================
# 6. Client Code
# ==========================================
def render_ui(factory: UIFactory):
    # The client code works with factories and products solely through 
    # abstract types, keeping it completely decoupled from concrete classes.
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    
    print(button.render())
    print(checkbox.render())


if __name__ == "__main__":
    print("--- Testing Windows Factory ---")
    windows_factory = WindowsFactory()
    render_ui(windows_factory)

    print("\n--- Testing Mac Factory ---")
    mac_factory = MacFactory()
    render_ui(mac_factory)
