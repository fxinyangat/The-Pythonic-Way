# Summary Checklist: 
# Which one should you use?Use @classmethod when your function needs to interact with 
# class-level attributes,
# call other class methods, or spin up new instances dynamically.
# Use @staticmethod 
# when your function represents a standalone utility that performs computation purely
# using the parameters provided to it.Use a standard instance method (using self) if 
# the logic needs to manipulate individual object data unique to each instance

from datetime import date

class Employee:
    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age
        
    @classmethod
    def from_birth_year(cls, name:str, birth_year:int):
        age = date.today().year - birth_year
        
        return cls(name, age)
    
    @classmethod
    def from_string(cls, emp_text:str):
        name,age = emp_text.split('-')
        return cls(name, int(age))
    
    @staticmethod
    def is_adult(age):
        return True if age > 18 else False
        
    
emp1 = Employee.from_birth_year("Alice", 1998)

emp2 = Employee.from_string("John-19")

print(emp2.name)
print(emp2.age)

print(Employee.is_adult(12))