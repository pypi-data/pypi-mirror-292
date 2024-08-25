import sys
import re
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import URLError

from rich import print
from statemachine import State, StateMachine

from automatic_spectral_acquisition.constants import *


def error_message(exception_type:str, message:str) -> None:
    """Print an error message if DEBUG is false. Otherwise, raise an exception.

    Args:
        exception_type (str): The type of the exception.
        message (str): The error message.

    Raises:
        exception_class: The exception class based on the exception_type.
    """
    if DEBUG:
        exception_class = globals().get('__builtins__').get(exception_type, Exception)
        if exception_class is not None:
            raise exception_class(message)
        else:
            raise Exception(message)
    else:
        print(f'[bold red]{exception_type}:[/bold red] {message}')
        print(f'[#969696]Switch DEBUG to True for a traceback when available.[/#969696]')
        sys.exit()
    
 
def info_message(message:str, type:str|None=None) -> None:
    """Print an informational message.

    Args:
        message (str): The message to be printed.
        type (str | None, optional): The type of the message. Defaults to None.
    """
    if type is not None:
        print(f'[bold purple]{type}:[/bold purple] {message}')
    else:
        print(message)


def save_diagram_to_file(sm:StateMachine, path:str=f'{TEMP_DIRECTORY}/statemachine_diagram.svg') -> None:
    """Save the diagram of the state machine to an SVG file.

    Args:
        sm (StateMachine): The state machine object.
        path (str): The path to save the SVG diagram file. Defaults to f'{TEMP_DIRECTORY}/statemachine_diagram.svg'.
    """
    dot_representation = sm._graph().to_string()
    dot_representation = re.sub(r'(?<=\d)pt', '', dot_representation) # remove 'pt' from font size
    url = f"https://quickchart.io/graphviz?graph={quote(dot_representation)}"

    try:
        response = urlopen(url)
        data = response.read()
    except URLError:
        error_message('URLError', 'Could not connect to the internet to generate the diagram.')
    
    with open(path, "wb") as f:
        f.write(data)

