# your_package_name/main.py

def greet(name):
    """Returns a greeting for the given name."""
    return f"Hello, {name}!"

class Calculator:
    """A simple calculator class."""
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a,b):
        return a*b
    
    def division(self, a,b):
        return a/b

class list_lib:
    
    def flatten_list(list_of_lists):
        # Use a list comprehension to flatten the list
        return [item for sublist in list_of_lists for item in sublist]

class string_op_lib:
    def count_char_frequency(s):
    frequency = {}  # Dictionary to store character frequencies
    
    # Loop through each character in the string
    for char in s:
        if char in frequency:
            frequency[char] += 1  # Increment the count for the character
        else:
            frequency[char] = 1  # Initialize the count for the character
    
    return frequency





    
# Make these functions/classes available for import
__all__ = ["greet", "Calculator", "list_lib", "string_op_lib"]
