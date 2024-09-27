import json

def sanitize_input(input):
    if isinstance(input, str):
        return json.loads(input)
    return input
