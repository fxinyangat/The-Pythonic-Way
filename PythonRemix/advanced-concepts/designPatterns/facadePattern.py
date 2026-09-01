"""
The Facade design pattern is a structural design pattern that provides a 
simplified interface to a complex subsystem of classes, librabry or framework.
Instead of making your client code interact with dozens of specialized classes,
the facade exposes a single straightforward class that manages the underlying complexity behind the scenes.

Core Components
*   Facade: The entry point class that knows which subsystem classes to route a request to and how to glue them together.
*   Complex Subsystem: A collection of diverse classes that handle intensive, low-level operations (e.g., rendering video, parsing file formats, or authenticating APIs).
*   Client: The application code that calls the Facade instead of triggering the complex subsystem directly.

When to Use It
*   Simplifying Complex APIs: When you need to integrate a massive third-party SDK or legacy 
system but only need 5% of its total functionality.
*   Layering Software: When you want to decouple an application layer. 
You can create a facade to act as the single entry point between a desktop
UI layer and a complex backend engine.
*   Reducing Dependencies: When your client code risks becoming tightly 
coupled to the implementation details of multiple external classes.
"""

# 1. Complex Subsystem Classes
class PopcornPopper:
    def turn_on(self): print("Popper: ON")
    def pop(self): print("Popper: Popping delicious popcorn")
    
class Lights:
    def dim(self, level:int): print(f"Lights dimmed to {level}")
    def turn_on(self): print("Lights: Brightness restored to 100%")
    
class Projector:
    def turn_on(self): print("Projector: ON")
    def set_input(self, source:str): print(f"Projector: Input set to {source}")
    
class SoundSystem:
    def turn_on(self): print("Sound System:ON")
    def set_volume(self, level:int):print(f"Sound System: Volume set to {level}")
    

#2. The Facade (Simplifies everything for the client)
class SmartHomeFacade:
    def __init__(self, popper:PopcornPopper, lights: Lights, projector: Projector, sound:SoundSystem):
        self.popper = popper
        self.lights = lights
        self.projector = projector
        self.sound = sound
        
    def watch_movie(self, movie_title:str):
        print(f"\n--- Getting ready to watch '{movie_title}' ---")
        self.popper.turn_on()
        self.popper.pop()
        self.lights.dim(10)
        self.projector.turn_on()
        self.projector.set_input("Blu-ray")
        self.sound.turn_on()
        self.sound.set_volume(20)
        print("--- Enjoy your movie! ---\n")
    
    def end_movie(self): 
        print(f"\n--- Cleaning up after watching movie ---")
        self.lights.turn_on()
        self.sound.set_volume(0)
        print("--- Hope You enjoyed your movie! ---\n")
        
    #. Client Code
    
if __name__ == "__main__": 
    # The client initializes the low-level components once (or a factory builds them)
    facade = SmartHomeFacade(PopcornPopper(), Lights(), Projector(), SoundSystem())
    
    # The client interacts only with a simple interface
    
    facade.watch_movie("Star Wars")
    facade.end_movie()
    
        
