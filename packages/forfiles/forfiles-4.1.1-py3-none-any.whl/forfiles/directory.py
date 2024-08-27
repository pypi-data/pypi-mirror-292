import os
from typing import Callable


def dir_action(
    path: str,
    print_paths: bool,
    fn: Callable[..., None],
    *args,
    **kwargs,
) -> None:
    """Iterates through a directory and executes a function for each file in the directory.

    Args:
        path (str):
            The path of the directory to iterate through.

        print_paths (bool):
            Whether or not to print the path of each file to the terminal during iteration.

        fn (Callable[..., None]):
            A callback function that will be called with each file as its argument.

        *args:
            Optional positional arguments that will be passed to the callback function.

        **kwargs:
            Optional keyword arguments that will be passed to the callback function.

    Returns:
        None. This function does not return any value.

    Raises:
        OSError: If the directory specified by 'path' does not exist or cannot be accessed.

    Examples:
        The following code demonstrates how to use dir_action to print the contents of a directory:

        >>> def print_file_contents(file_path):
        ...     with open(file_path, 'r') as file:
        ...         print(file.read())

        >>> dir_action('/path/to/directory', True, print_file_contents)

        This will print the contents of each file in the directory '/path/to/directory', as well as its path.
    """

    for root, _, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if print_paths:
                print(file_path.replace("\\", "/"))
            fn(file_path, *args, **kwargs)
