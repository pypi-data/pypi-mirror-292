import os
from shutil import rmtree


def filter_type(directory: str, file_types: list, blacklist_mode: bool = False):
    """
    Filters files in a directory based on their file type

    Args:
        directory (string): full path to the directory where the files will be filtered
        desired_file_types (list): file type extensions that will be kept, for example: [".png", ".txt"]
        blacklist_mode (bool): by default the listed file types are kept, if this is set to true, the listed file types will be removed and other remaining files will be kept

    Returns:
        void
    """

    for file_type in file_types:
        if not file_type.startswith("."):
            file_type = f".{file_type}"

    for subdir, _, files in os.walk(directory):

        for file in files:
            if blacklist_mode and file.endswith(tuple(file_types)):
                os.remove(f"{os.path.abspath(subdir)}/{file}")
            elif not file.endswith(tuple(file_types)):
                os.remove(f"{os.path.abspath(subdir)}/{file}")


def dir_create(dir_path: str):
    """Creates directory is it does not exist previously

    Args:
        dir_path (str): path of the directory that will be created
    """
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)


def dir_delete(dir_path: str):
    """Deletes directory and its contents if it exists.

    Args:
        dir_path (string): path of the directory that will be deleted
    """
    if os.path.isdir(dir_path):
        rmtree(dir_path)


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')

    filter_type(f"{home_dir}/filter-test", [".png", ".txt", "md"])
