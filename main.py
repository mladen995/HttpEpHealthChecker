"""HTTP endpoints health checker

This script allows the user to check the health of desired HTTP endpoints by testing their availability.
HTTP endpoints for testing are set in a configuration file that must be of type (.yaml).
The configuration file is assumed to be well formatted.

This script requires `requests', `keyboard' and `pyyaml` to be installed inside Python
the environment in which you run this script.

This file can also be imported as a module and contains the following
functions:

    * usage - the usage function which shows how to run this program properly
    * main - the main function of the script
"""
import sys
import getopt
import os
from http_request import CheckEndPointsHealth
from utils.common import CheckIsFileValid, LoadYamlFile



def usage():
    '''
    Print help how to run program properly in terminal

            Returns:
                    None                  

    '''
    print("usage: python main.py -f/--filepath <FILEPATH>")

def main(argv: str):
    '''
    Main program function which uses command line argument for running

            Parameters:
                    argv (str): File path for validation

            Returns:
                    None
                    

    '''
    # Exit from program if user inserts more than two arguments
    if len(argv) > 2:
        usage()
        sys.exit()

    # Validate arguments from the command line
    try:
        option, arguments = getopt.getopt(argv,"hf:",["help","filepath="])
    except getopt.GetoptError as error:
        print(error)
        sys.exit()
    # Proceed further regarding user selected option (-f or -h)
    for opt, variable in option:
        # Help option
        if opt in ("-h", "--help"):
            usage()
        # Program initiated option
        elif opt in ("-f", "--filepath"):
            # Normalize the specified path
            filepath = os.path.normpath(variable)
            # Check if configuration file is valid
            is_valid, message = CheckIsFileValid(filepath)
            if is_valid:
                # Load data from configuration file
                data = LoadYamlFile(filepath)
                # Initiate health checker for parsed data
                CheckEndPointsHealth(data)
            else:
                print(message)
                usage()
                sys.exit()
        # Unsupported option
        else:
            usage()
            sys.exit()

# Starting point when user runs program with the proper arguments
if __name__ == '__main__':
    main(sys.argv[1:])