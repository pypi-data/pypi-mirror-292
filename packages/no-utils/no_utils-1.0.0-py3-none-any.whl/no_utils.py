"""
no_utils.py

This module provides various utilities for performing common tasks such as executing system commands, 
guarding against None and empty variables, and manipulating files.
"""

import sys
import os
from subprocess import Popen, PIPE
from typing import List, Tuple, Union
import contextlib
import inspect

def system_cmd(command: str) -> Tuple[int, str, str]:
    """
    Execute a system command and return its exit code, standard output, and standard error.

    Parameters:
    - command (str): The system command to execute.

    Returns:
    - tuple: A tuple containing the exit code (int), standard output (str), and 
      standard error (str).
    """
    with Popen(args=command, stdout=PIPE, stderr=PIPE, shell=True) as process:
        out, err = process.communicate()
        retcode = process.poll()
    return retcode, out.decode("utf-8"), err.decode("utf-8")

class Guard:
    """
    A utility class for guarding against None and empty variables.

    Methods:
    - against_none(var, force_exit=True): Check if the variable is None and optionally 
      exit the program.
    - against_empty(var, force_exit=True): Check if the variable is empty and optionally 
      exit the program.
    - against_empty_str(var, force_exit=True): Check if the string is empty and optionally
      exit the program.
    - against_stuck_thread(thread, timeout, kill_instead=False, force_exit=True): Check if
      the thread is stuck and optionally exit the program.
    """

    def against_none(self, var: Union[None, any], throw_exception: bool = False, force_exit: bool = True) -> None:
        """
        Check if the variable is None and optionally exit the program.

        Parameters:
        - var: The variable to check.
        - throw_exception (bool): Whether to throw an exception instead of exiting the program. 
          Default is False.
        - force_exit (bool): Whether to exit the program if the variable is None. 
          Default is True.
        """
        if var is None:
            print("Supplied variable is None!")
            if throw_exception:
                raise ValueError("Supplied variable is None!")
            if force_exit:
                sys.exit(-1)

    def against_empty(self, var: Union[list, dict, set, tuple], throw_exception:bool = False, force_exit: bool = True) -> None:
        """
        Check if the variable is empty and optionally exit the program.

        Parameters:
        - var (list, dict, set, tuple): The variable to check.
        - throw_exception (bool): Whether to throw an exception instead of exiting the program. 
          Default is False.
        - force_exit (bool): Whether to exit the program if the variable is empty. 
          Default is True.
        """
        if not var:
            print("Supplied variable is empty!")
            if throw_exception:
                raise ValueError("Supplied variable is empty!")
            if force_exit:
                sys.exit(-1)

    def against_empty_str(self, var: str, throw_exception:bool = False, force_exit: bool = True) -> None:
        """
        Check if the string is empty and optionally exit the program.

        Parameters:
        - var (str): The string to check.
        - throw_exception (bool): Whether to throw an exception instead of exiting the program. 
          Default is False.
        - force_exit (bool): Whether to exit the program if the string is empty. 
          Default is True.
        """
        if not var.strip():
            print("Supplied string is empty!")
            if throw_exception:
                raise ValueError("Supplied string is empty!")
            if force_exit:
                sys.exit(-1)

class FileUtils:
    """
    A utility class for performing various file operations such as replacing text,
    clearing content, appending data, checking for content existence, and manipulating lines.

    Methods:
    - replace(file_path, old_str, new_str, encoding='utf-8'): Replace occurrences of old_str 
      with new_str in the specified file.
    - clear(file_path, encoding='utf-8'): Clear the content of the specified file.
    - append(file_path, data, encoding='utf-8'): Append data to the specified file.
    - content_exists(file_path, content, encoding='utf-8'): Check if the specified content 
      exists in the file.
    - get_lines_with_content(file_path, content, encoding='utf-8'): Get lines from the file 
      that contain the specified content.
    - get_lines_without_content(file_path, content, encoding='utf-8'): Get lines from the file 
      that do not contain the specified content.
    - remove_empty_lines(file_path, encoding='utf-8'): Remove all empty lines from the specified file.
    - remove_last_empty_line(file_path, encoding='utf-8'): Remove the last empty line from the 
      specified file.
    - merge_files(file_paths, output_path, encoding='utf-8'): Merge the specified files into a 
      single file.
    """

    def replace(self, file_path: str, old_str: str, new_str: str, encoding: str = 'utf-8') -> None:
        """Replace occurrences of old_str with new_str in the specified file."""
        with open(file_path, 'r', encoding=encoding) as file:
            filedata = file.read()

        newdata = filedata.replace(old_str, new_str)

        with open(file_path, 'w', encoding=encoding) as file:
            file.write(newdata)

    def clear(self, file_path: str, encoding: str = 'utf-8') -> None:
        """Clear the content of the specified file."""
        with open(file_path, 'w', encoding=encoding) as file:
            file.write("")

    def append(self, file_path: str, data: str, encoding: str = 'utf-8') -> None:
        """Append data to the specified file."""
        with open(file_path, 'a', encoding=encoding) as file:
            file.write(data)

    def content_exists(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Check if the specified content exists in the file."""
        with open(file_path, 'r', encoding=encoding) as file:
            filedata = file.read()

        return content in filedata

    def get_lines_with_content(self, file_path: str, content: str, encoding: str = 'utf-8') -> List[str]:
        """Get lines from the file that contain the specified content."""
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        return [line for line in lines if content in line]

    def get_lines_without_content(self, file_path: str, content: str, encoding: str = 'utf-8') -> List[str]:
        """Get lines from the file that do not contain the specified content."""
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        return [line for line in lines if content not in line]

    def remove_empty_lines(self, file_path: str, encoding: str = 'utf-8') -> None:
        """Remove all empty lines from the specified file."""
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        lines = [line for line in lines if line.strip() != ""]

        with open(file_path, 'w', encoding=encoding) as file:
            file.writelines(lines)

    def remove_last_empty_line(self, file_path: str, encoding: str = 'utf-8') -> None:
        """Remove the last empty line from the specified file."""
        with open(file_path, 'r', encoding=encoding) as file:
            lines = file.readlines()

        if lines and lines[-1].strip() == "":
            lines = lines[:-1]

        with open(file_path, 'w', encoding=encoding) as file:
            file.writelines(lines)

    def merge_files(self, file_paths: List[str], output_path: str, encoding: str = 'utf-8') -> None:
        """Merge the specified files into a single file."""
        with open(output_path, 'w', encoding=encoding) as output_file:
            for file_path in file_paths:
                with open(file_path, 'r', encoding=encoding) as file:
                    output_file.write(file.read())

class FolderUtils:
    """
    A utility class for performing various folder operations such as changing the current working directory.

    Methods:
    - change_dir(new_dir): Context manager to change the current working directory to the specified directory.
    - cwd_here(): Set the current working directory to the script that calls this function.
    """

    @contextlib.contextmanager
    def change_dir(self, new_dir: str):
        """
        Change the current working directory to the specified directory.

        Parameters:
        - new_dir (str): The new directory to change to.
        """
        old_dir = os.getcwd()
        os.chdir(new_dir)
        try:
            yield
        finally:
            os.chdir(old_dir)

    def cwd_here(self):
        """
        Set the current working directory to the script that calls this function.
        """
        os.chdir(os.path.dirname(inspect.stack()[1].filename))
