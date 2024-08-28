from input_plus.input_regex import input_regex


def input_integer(prompt: str) -> int:
    '''
    A function that takes a prompt and returns an integer.

    Args:
        Prompt: The prompt to display to the user.
    '''
    value = input_regex(prompt, r'\-?\d*', force_match=True)
    if value == '' or value == '-':
        return 0
    return int(value)