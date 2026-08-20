"""
Builder pattern is a creational pattern that allows you to construct compalex objects 
step by step. It separates representation of an object from its construction
logic, making the code much cleaner when the object requires many optional
config parameters

Instead of creating a giant constrctor with a long list of positional args (often called the
"telescoping constructor" anti-pattern), you see a dedicated Builder class
that provides human-readable, chainable methods to set properties one by one.

Key Companents
*   Product: the complex object you want to create
*   Builder Interface/Abstract Class: Defines the mandatory building steps
*   Concrete Builder: Implements the steps and tracks the state of the product
*   Director (Optional) : Controls the order of the building steps to create specific, predeifined product configs

When to Use This PatternMassive Constructors: 
*   When your object initialization contains more than 4 or 5 parameters.
*   Step-by-step assembly required: When parts must be built sequentially or depend on explicit configurations.
*   Immutability representation: When an object should remain unchangeable (immutable) once it's created,
but requires configuration changes during set-up
"""

class DesktopComputer:
    def __init__(self):
        self.cpu = "Standard CPU"
        self.ram = "8GB DDR4"
        self.gpu = "Integrated Graphics"
        self.storage = "512GB SSD"
        
    def __str__(self):
        return f"Computer Specs [CPU: {self.cpu}, RAM: {self.ram}, GPU: {self.gpu}, Storage: {self.storage}]"

class ComputerBuilder:
    def __init__(self):
        self.computer = DesktopComputer()
        
    def set_cpu(self, cpu_model:str):
        self.computer.cpu = cpu_model
        return self #enables method chaining
    
    def set_ram(self, ram_size:str):
        self.computer.ram = ram_size
        return self
    
    def set_gpu(self,gpu_model:str):
        self.computer.gpu = gpu_model
        return self
    
    def set_storage(self, storage_Size:str):
        self.computer.storage = storage_Size
        return self
    
    def build(self)->DesktopComputer:
        # add validation logic here before returning
        if "RTX" in self.computer.gpu and "8GB" in self.computer.ram:
            print("Warning: 8GB might bottleneck an RTX GPU")
            
        return self.computer

if __name__ == "__main__":
    gaming_pc = (
        ComputerBuilder()
        .set_cpu("Intel i9")
        .set_ram("32GB DDR5")
        .set_gpu("NVIDIA RTX 4090")
        .set_storage("2TB NVMe SSD")
        .build()
    )
    # Build a budget machine using mostly defaults
    budget_pc = (
        ComputerBuilder()
        .set_cpu("AMD Ryzen 3").set_ram("8GB").set_gpu("RTX")
        .build()
    )
    
    
    
    print(f"Gaming PC\n {gaming_pc}")
    print(f"Budget PC\n {budget_pc}")
    
    # Advanced Topics
    # - Director class
    # - Embed this into an abstract factory style builder t osupport different structures
    