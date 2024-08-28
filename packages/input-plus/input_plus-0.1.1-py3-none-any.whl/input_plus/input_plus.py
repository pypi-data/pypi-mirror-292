import msvcrt
import re
import sys
from typing import Callable, Tuple


def input_plus(printer: Callable[[str], None],
               selector: Callable[[str], Tuple[bool, str]],
               validator: Callable[[str], bool] = None,
               special_actions: Callable[[bytes], None] = None) -> str:
    '''
    A function that allows for more advanced input handling than the built-in input function.

    Args:
        Printer: A function that takes a string and prints it to the console.
        Selector: A function that takes a string and returns a tuple of a boolean and a string.
        The boolean indicates if the return string is valid, and the string is the value to return.
        Validator: A function that takes a string and returns a boolean indicating if the input is valid.
        Special Actions: A function that takes a byte and performs a special action based on the input.
    '''
    input_string = ''
    printer(input_string)
    while True:
        input_char = msvcrt.getwch() # Get the input character
        is_special_key = False

        # Special actions
        if input_char == '\x00' or input_char == '\xe0':
            is_special_key = True
            input_char += msvcrt.getwch()

        char_code = input_char.encode()
        # Control characters
        if char_code == b'\x03': # Ctrl+C
            print()
            sys.exit(1)

        elif char_code == b'\x0d': # Enter key
            is_valid, value = selector(input_string)
            if is_valid:
                print()
                return value

        elif char_code == b'\x08': # Backspace
            input_string = input_string[:-1]

        elif char_code == b'\x17': # Ctrl+Backspace
            input_string = re.sub(r'((?<=\s)|(?<=^))\w*\s?$', '', input_string)

        elif is_special_key: # Special keys
            if special_actions is not None:
                special_actions(char_code)

        else:
            if validator is None or validator(f'{input_string}{input_char}'):
                input_string += input_char

        printer(input_string)