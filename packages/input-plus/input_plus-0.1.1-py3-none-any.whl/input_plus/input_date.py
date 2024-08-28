from input_plus.input_regex import input_regex


import re
from datetime import datetime


def input_date(prompt: str, strptime_format = "%Y-%m-%d") -> datetime:
    '''
    A function that allows the user to input a date using a strptime format string.

    Args:
        prompt: The prompt to display to the user.
        strptime_format: The strptime format string to use for parsing the date.
    '''
    # Converts the strptime format to a regex format
    format_mappings  = {
        '%Y': {'regex': r'\d{4}', 'readable': 'YYYY'},
        '%m': {'regex': r'0[1-9]|1[0-2]', 'readable': 'MM'},
        '%d': {'regex': r'0[1-9]|[12]\d|3[01]', 'readable': 'DD'}
    }

    regex = re.escape(strptime_format)
    readable = strptime_format

    for strp_format, mapping in format_mappings.items():
        regex = regex.replace(re.escape(strp_format), f'({mapping['regex']})')
        readable = readable.replace(strp_format, mapping['readable'])

    result = input_regex(prompt, regex, force_match=False, warn_error=True, placeholder=readable)
    return datetime.strptime(result, strptime_format).date()