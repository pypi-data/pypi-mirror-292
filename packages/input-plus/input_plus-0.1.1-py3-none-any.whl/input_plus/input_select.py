from input_plus.input_plus import input_plus
import Levenshtein


from colorama import Fore, Style


def input_select(prompt: str, options: list, list_size: int = 5) -> str:
    '''
    A function that allows for selecting an option from a list of options.

    Args:
        Prompt: The prompt to display before the input.
        Options: A list of strings representing the options to select from.
        List Size: The number of options to display at once.
    '''
    height = 0
    select_index = 0
    offset = 0

    def get_options_scores(input_string):
        # get the levenstein distance of each option
        option_scores = [{'option': option, 'score': Levenshtein.distance(input_string, option)} for option in options]
        # sort the options by score descending
        option_scores = sorted(option_scores, key=lambda x: x['score'])
        # get the top list_size options
        option_scores = option_scores[offset:list_size + offset]
        return option_scores

    def _printer(input_string):
        nonlocal height, list_size, select_index, offset

        MOVE_TO_START = '\r' # Move the cursor to the start of the line
        CURSOR_FORWARD = '\x1b[C' # Move the cursor forward one character
        CLEAR_LINE = '\033[J' # Clear the current line

        # store all text to print to remove flickering
        to_print = ''

        # Clear previous lines
        to_print += f'{MOVE_TO_START}{CLEAR_LINE}' * height

        to_print += f'{prompt}{input_string}\n'

        option_scores = get_options_scores(input_string)

        for i, option_score in enumerate(option_scores):
            temp_text = ''
            if i < len(option_scores) - 1:
                temp_text = f'  {option_score['option']}\n'
            else:
                temp_text = f'  {option_score['option']}'

            if i == select_index:
                temp_text = f'{Fore.GREEN}{temp_text}{Style.RESET_ALL}'

            to_print += temp_text

        height = len(option_scores)

        # Move cursor back to the beginning of the input
        to_print += f'\033[A' * height
        to_print += f'{MOVE_TO_START}{CURSOR_FORWARD * len(f'{prompt}{input_string}')}'

        print(to_print, end='', flush=True)

    def _selector(input_string):
        nonlocal height, select_index

        MOVE_TO_START = '\r' # Move the cursor to the start of the line
        CLEAR_LINE = '\033[J' # Clear the current line

        # store all text to print to remove flickering
        to_print = ''

        # Clear previous lines
        to_print += f'{MOVE_TO_START}{CLEAR_LINE}' * height
        to_print += MOVE_TO_START

        option_scores = get_options_scores(input_string)
        return_value = option_scores[select_index]['option']

        to_print += f'{prompt}{return_value}'

        print(to_print, end='', flush=True)
        return True, return_value

    def _special_actions(char_code):
        nonlocal select_index, offset

        if char_code == b'\xc3\xa0H': # Up arrow
            if select_index > 0:
                select_index = max(select_index - 1, 0)
            else:
                offset = max(offset - 1, 0)
        elif char_code == b'\xc3\xa0P': # Down arrow
            if select_index < list_size - 1:
                select_index = min(select_index + 1, list_size - 1)
            else:
                offset = min(offset + 1, len(options) - list_size)

    return input_plus(_printer, _selector, special_actions=_special_actions)