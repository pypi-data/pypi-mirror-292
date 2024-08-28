from input_plus.input_regex import input_regex


def input_float(prompt: str) -> float:
    '''
    A function that takes a prompt and returns a float.

    Args:
        prompt: The prompt to display to the user.
    '''
    value = input_regex(prompt, r'\-?\d*\.?\d*?', force_match=True)
    if value == '' or value == '-' or value == '.':
        return 0
    return float(value)