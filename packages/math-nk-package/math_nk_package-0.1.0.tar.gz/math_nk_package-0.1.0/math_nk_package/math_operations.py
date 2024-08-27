def add(*args):
    try:
        return sum(args)
    except TypeError:
        return "Error: All inputs must be numbers."

def subtract(*args):
    try:
        if len(args) < 1:
            return "Error: At least one number is required."
        result = args[0]
        for num in args[1:]:
            result -= num
        return result
    except TypeError:
        return "Error: All inputs must be numbers."

def multiply(*args):
    try:
        result = 1
        for num in args:
            result *= num
        return result
    except TypeError:
        return "Error: All inputs must be numbers."

def evaluate(expression):
    try:
        return eval(expression)
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        return f"Error: {str(e)}"

