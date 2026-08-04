"""
In Python, a dataclass is a regular class that uses the @dataclass decorator 
to automatically generate boilerplate methods like __init__, __repr__, and __eq__.
They are primarily used as containers for data with minimal logic.Key FeaturesAutomatic 
Methods: Generates common "dunder" methods based on the class attributes
you define.Type Annotations: Requires fields to be defined as class variables with type hints.
Immutability: Setting frozen=True makes the instance read-only 
after creation.Default Values: Allows you to assign default values to attributes easily
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ModelConfig:
    model_name: str
    temperature: float
    max_tokens: int = 200
    
    # optional fuels
    stop_sequence: Optional[list[str]] = None
    api_headers: dict = field(default_factory=lambda:{"Content-Type": "application/json"})
    
    def __post_init__(self):
        # validation logic
        
        if not(0 <= self.temperature <= 1):
            raise ValueError("Temperature must be between 0 and 1")
        print(f"Config for {self.model_name} initialized successfully")

my_class = ModelConfig("gemini-3.1-pro",0.4, 300,{"Content-Type":"json"})

print(my_class.api_headers)