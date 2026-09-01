"""
The Singleton PAttern is a creational design pattern that restricts a class
to a single instance and provides a global access point.

While you can write custom singleton classes using __new__ or metaclasses,
the most idiomatic, threadsafe way to achieve a singleton in Python is by 
leveraging Python Modules.

Below are the three ways to implement a singleton pattern in Python.
"""

# Method 1: The Native Module Approach (Recommended)
""" Python modules are naturally singletons. When a module is imported for the first
time, python runs the code and catches the result in sys.modules.
Every subsequent import across your application simply returns that same 
catched reference.



"""
# STEP 1: Define your service and instantiate it in the dedicated file

# database.py

class DatabaseConnection:
    def __init__(self):
        self.connected =True
        self.query_count = 0
        
    def execute_query(self, sql:str):
        self.query_count += 1
        return f"Executing: {sql}"
    
#Always instanctiate the object directly inside the module
db_instance = DatabaseConnection() 

#STEP 2: Import the precreated instance anywhere you need it

# main.py

# from database import db_instance
print(db_instance.execute_query("SELECT * from users"))

# Every file importing db_instance shares the exact same state


#METHOD 2: Overiding __new__ (the classic class approach)
"""
If you prefer to use the standard object creation syntax (Class()) 
while enforcing a singleton, override the dunder method __new__, 
which controls how new instances are allocated in memory.
"""

class ClassicSingleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        # create new instance only if not exists
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self, value:str=None):
        # Guard clasue to prevent __init__ from re-initializating properties
        if not hasattr(self, "_initialized"):
            self.value = value
            self._initialized = True
            
#verification

obj1 = ClassicSingleton("first Call")
obj2 = ClassicSingleton("Sencond call")

print(obj1)
print(obj2.value)
print(obj1 is obj2)
print(obj1.value)

# Advecned concept : Method 3:  The Metaclass Approach (Cleanest Class Separation)
