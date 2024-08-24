# -*- coding: utf-8 -*-
"""
Simple module containing several functions that wrap some of Pythons IO functionalities for handling text files.
Mainly intended for teaching purposes.
"""

def listReadValues(fileName: str) -> list[float]:
    """ 
    Function to read numbers from a file and return a list of floats.

    Parameters
    ----------
    fileName : str
        The path (full path or relative path) of the file to read.

    Returns
    -------
    list
        A list of floats, with each float representing a number from the file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file contains non-numeric values.

    """
    file = open(fileName, mode='r', encoding="utf-8")
    value_str_list = file.read().splitlines()
    file.close()
    value_float_list = []
    for value_str in value_str_list:
        value_float_list.append(float(value_str))
    return value_float_list

def listRead(fileName: str) -> list[str]:
    """ 
    Function to read text from a file and return a list of strings (one string per line).

    Parameters
    ----------
    fileName : str
        The path (full path or relative path with respect to the working directory) 
        of the file to read.

    Returns
    -------
    list[str]
        A list of strings, where each string represents a line from the file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IOError
        If there is an error while reading the file.

    """
    name_file = open(fileName, mode='r', encoding="utf-8")
    mylist = name_file.read().splitlines() 
    name_file.close()
    return mylist
    
def stringRead(fileName: str) -> str:
    """ 
    Function to read text from a file and return it as a single string.

    Parameters
    ----------
    fileName : str
        The path (full path or relative path with respect to the working directory) 
        of the file to read.

    Returns
    -------
    str
        The contents of the file as a single string.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.

    IOError
        If there is an error while reading the file.

    """
    name_file = open(fileName, mode='r', encoding="utf-8")
    mystring = name_file.read().strip()
    name_file.close()
    return mystring
    
def listWrite(fileName: str, list_of_strings: list[str]) -> None:
    """Write a list of strings to a text file (one line per string).

    Parameters
    ----------
    fileName : str
        The path (full path or relative to the working directory) of the file that will be created. 
        If the file already exists, it will be overwritten.

    list_of_strings : list[str]
        A list of strings to be written to the file.

    Returns
    -------
    None
        This function does not return anything.

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist.

    PermissionError
        If the user does not have permission to write to the specified file.

    """
    name_file = open(fileName, mode='w', encoding="utf-8")
    name_file.write('\n'.join(list_of_strings))
    name_file.close()
    
def stringWrite(fileName: str, mystring: str) -> None:
    """
    Writes the given string to a file with the specified file name.

    Parameters
    ----------
    fileName (str):
        The name of the file to write to.

    mystring (str):
        The string to write to the file.

    Returns
    -------
    None
        This function returns nothing

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist.

    PermissionError
        If the user does not have permission to write to the specified file.  

    """
    name_file = open(fileName, mode='w', encoding="utf-8")
    name_file.write(mystring)
    name_file.close()
    return None
