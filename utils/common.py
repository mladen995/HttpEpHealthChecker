""" Handle file related operations

This module is imported by the main script for file manipulation purposes


    * CheckIsFileValid - function for checking validity of given file_path
    * LoadYamlFile - function for loading data from (.yaml) file

"""
import os
import yaml

def CheckIsFileValid(file_path: str):
    '''
    Checking file validity from given file path

            Parameters:
                    file_path (dict): File path for validation

            Returns:
                    tuple(bool, str): Validity status and status description
                    

    '''
    # Check if path exists
    if not os.path.exists(file_path):
        return False, "file_path does not exist."

    # Check if the path is a file
    if not os.path.isfile(file_path):
        return False, "file_path does not point to a file."

    # Check read permission
    if not os.access(file_path, os.R_OK):
        return False, "No read permission for the file."

    return True, "File exists and is readable."

def LoadYamlFile(file_path: str):
    '''
    Loading data from (.yaml) file to dictionary

            Parameters:
                    file_path (dict): File for reading data

            Returns:
                    data (dict): Loaded data

            Raises: SystemExit is triggered if (.yaml) file has wrong format

    '''
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(e)
            raise SystemExit