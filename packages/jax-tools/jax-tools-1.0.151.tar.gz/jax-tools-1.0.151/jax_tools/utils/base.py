# -*- coding:utf-8 -*-
"""
utils base
"""
from typing import TypeVar
import re
import sys

KT = TypeVar('KT')
VT = TypeVar('VT')


def sanitize_input(input_string: str) -> str:
    """
    Sanitizes an input string by escaping potentially dangerous characters.

    Args:
        input_string (str): The string to be sanitized.

    Returns:
        str: The sanitized string.
    """

    # 移除或转义特殊字符
    sanitized = re.sub(r'[;|&`\'\"*?~<>^()[\]{}$\\]', '', input_string)
    return sanitized


def chinese_double_length(string: str) -> int:
    """
    Get string length, chinese double length
    Args:
        string (str): string for calculate length

    Returns:
        int: string length
    """
    length = 0
    for char in string:
        if ord(char) > 127:  # 如果字符的ASCII码大于127，则认为是中文字符
            length += 2
        else:
            length += 1
    return length


def get_input(prompt: str) -> str:
    """
    Get input from user with a prompt.
    Args:
        prompt (str): The prompt to display to the user.

    Returns:

    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    input_string = ''
    try:
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
    except ModuleNotFoundError:
        return input(prompt)
    try:
        import tty
        tty.setcbreak(sys.stdin.fileno())
        while True:
            char = sys.stdin.read(1)
            if char == '\r' or char == '\n':
                sys.stdout.write('\n')
                return input_string
            # Backspace character
            elif char == '\x08':
                if len(input_string) > 0:
                    input_string = input_string[:-1]
                    # Move cursor back and erase character
                    sys.stdout.write('\b \b')
            else:
                input_string += char
                sys.stdout.write(char)
            sys.stdout.flush()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == '__main__':
    print(chinese_double_length('aa bb'))