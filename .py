
# Calculator structure

class Calculator:
    def __init__(self, number1, number2):
        self.number1 = number1
        self.number2 = number2
        self.result = 0.0

# Arithmetic functions

def add(num1, num2):
    return num1 + num2

def subtract(num1, num2):
    return num1 - num2

def multiply(num1, num2):
    return num1 * num2

def divide(num1, num2):
    if num2 != 0:
        return num1 / num2
    else:
        return 'Cannot divide by zero'
