
from functools import wraps
def clean_prompt(func):
    @wraps(func)
    def wrapper(text, *args, **kwargs):
        cleaned_text = text.strip().lower()

        print(f"Cleaning input '{text} -> {cleaned_text}'")

        result = func(cleaned_text, *args, **kwargs)

        return f"{result}\n Processing Done"
    return wrapper

    

@clean_prompt
def call_llm(prompt):
    print("Sending prompt to API")
    """Says hello to the user."""

    return f"Response to: {prompt}"

print(call_llm("HELLO WORLD"))

# @property Decorator
# built in tool uesed to turn a method inot an attribute.


class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def diameter(self):
        return self.radius * 2
c = Circle(5)

print(c.diameter)

