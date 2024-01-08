""" HTTP requests handler

This module is imported by the main script for handling main program logic
of sending HTTP requests to the server, analyzing results and displaying
results to the command line.


    * CheckEndPointsHealth - main function for testing HTTP endpoints and displaying test results
    * SetUrlDomainGroups - function for organizing HTTP endpoints, in separate groups, depending on regarding url domain 
    * SendHttpRequest - function for sending HTTP request on endpoint
    * SendAllHttpRequests - function for sending all the HTTP requests from the configuration file
    * IsOutcomeUp - function for determinating outcome of each sent HTTP request
    * CalcAvailabilityPercentage - function for calculating availability percentage
"""
import time
import requests
import sys

# Global constants
DEFAULT_HTTP_METHOD = 'GET' # Default HTTP method
DEFAULT_HTTP_HEADERS = '' # Default HTTP request header
DEFAULT_HTTP_BODY = '' # Default HTTP request body

UP_START_CODE = 200 # lower end of HTTP status code for UP outcome
UP_END_CODE = 299 # upper end of HTTP status code for UP outcome
UP_MAX_LATENCY_MS = 500 # HTTP request latency from server response in millisconds
HTTP_REQ_TIMEOUT_S = 0.5 # HTTP request timeout in seconds (for optimal solution this should be equivalent to UP_MAX_LATENCY_MS)

CYCLE_DELAY = 15 # Cycle delay in seconds
# End of Global constants

def CheckEndPointsHealth(data_from_yaml: dict, delay: int = CYCLE_DELAY):
    '''
    Runs the health check for HTTP endpoints, every `n` seconds, and logs results to the console

            Parameters:
                    data_from_yaml (dict): Data for testing on form of dictionary
                    delay (int): Delay time in seconds for next cycle of testing

            Returns:
                    None

            Raises: SystemExit is triggered when user sendS keyboard interrupt with CTRL-C

    '''
    # Run program until user presses CTRL-C
    try:
        # Prepare recevied data for further processing
        urls = SetUrlDomainGroups(data_from_yaml)
        # Run program forever
        while True:
            # Send all HTTP requests
            SendAllHttpRequests(urls)
            for url_domain, data in urls.items():
                # Get health rate for url domain
                health_rate = CalcAvailabilityPercentage(data["total_outcome_up"], data["total_requests"])
                # Print result
                print(url_domain + " has " + str(health_rate) + "% availablity percentage")

            # Add a delay
            time.sleep(delay)
    # Catch CTRL-C and exit the program
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
        raise SystemExit


def SetUrlDomainGroups(data_from_yaml: dict):
    '''
    Grouping HTTP endpoints by regarding URL domain

            Parameters:
                    data_from_yaml (dict): Parsed data from configuration file

            Returns:
                    urls (dict): Reorganized data prepared for further processing

    '''
    # New data which will store relevant data but grouped by url domain
    urls = {}
    protocol_separator = '//'
    uri_path_separator = '/'
    # Loop through every endpoint
    for endpoint in data_from_yaml:
        # Check url domain from endpoint
        if 'url' in endpoint:
            # Extract url domain from complete web url
            try:
                # Remove protocol tags prefix
                after_protocol_string = endpoint['url'].split(protocol_separator)[1]
                # Remove url domain sufix
                url_domain = after_protocol_string.split(uri_path_separator)[0]
            except:
                print("Wrong web url format!")
                sys.exit()
            # If current url domain does not exist in the set of reorganized data then create the new one
            if url_domain not in urls:
                """
                Reorganized data structure:
                key -> url domain
                value -> [data, total_requests, total_outcome_up]
                    data: list of all relevant data for single endpoint which belongs to url domain
                    total_requests: counter of total HTTP requests sent to url domain
                    total_outcome_up: counter of total UP outcomes for all HTTP requests sent to url domain 
                """
                urls[url_domain] = {"data": [], "total_requests" : 0, "total_outcome_up" : 0}
            # Append data list with endpoint relevant data    
            urls[url_domain]["data"].append(endpoint)
    # return new formated data
    return urls

def SendHttpRequest(endpoint: dict, timeout: float = HTTP_REQ_TIMEOUT_S):
    '''
    Send HTTP request to endpoint

            Parameters:
                    endpoint (dict): Endpoint relevant data
                    timeout (float): Timeout for HTTP request

            Returns:
                    outcome (bool): Outcome for HTTP request

    '''
    # Map request methods with belonging HTTP methods
    request_functions = {
        "POST": requests.post,
        "PUT": requests.put,
        "DELETE": requests.delete,
        "GET": requests.get
    }

    # Set default value for each relevant endpoint data which is omitted in config file
    method = DEFAULT_HTTP_METHOD if "method" not in endpoint else endpoint["method"]
    headers = DEFAULT_HTTP_HEADERS if "headers" not in endpoint else endpoint["headers"]
    body = DEFAULT_HTTP_BODY if "body" not in endpoint else endpoint["body"]

    # Check if HTTP method for endpoint is valid
    if method in request_functions:
        # Assign request function for given HTTP method
        request_func = request_functions[method]
        try:
            # Send HTTP request
            r = request_func(endpoint["url"], data=body, headers=headers, timeout=timeout)
        # Handle exception for sent HTTP request
        except:
            # Here we are sure that response is either not received in expected time or any other error on the server has occured
            return False
        # We need to calculate if response outcome is UP or DOWN
        status_code = r.status_code
        # Convert server latency in ms
        latency_ms = round(r.elapsed.total_seconds(), 3) * 1000
        # Return outcome status for sent HTTP request
        return IsOutcomeUp(status_code, latency_ms)

def SendAllHttpRequests(urls: dict):
    '''
    Send HTTP request to all endpoints from urls data

            Parameters:
                    urls (dict): Data for sending

            Returns:
                    None

    '''
    # Send all HTTP requests to grouped by url domains
    for url_domain, data in urls.items():
        for endpoint in data["data"]:
            is_up_req = SendHttpRequest(endpoint)
            if is_up_req:
                # Increment counter for UP outcomes
                data["total_outcome_up"] += 1
            # Increment counter for total requests
            data["total_requests"] += 1

def IsOutcomeUp(status_code: int, response_time: int):
    '''
    Determination of outcome for sent HTTP request

            Parameters:
                    status_code (int): HTTP response status code
                    response_time (int): HTTP response time

            Returns:
                    outcome (bool): Outcome for sent HTTP request

    '''
    # Return outcome
    return (UP_START_CODE <= status_code <= UP_END_CODE) and response_time < UP_MAX_LATENCY_MS
    
def CalcAvailabilityPercentage(outcome_up_counter: int, total_req_counter: int):
    '''
    Calculating HTTP endpoint availability percentage

            Parameters:
                    outcome_up_counter (int): Counter for UP outcomes
                    total_req_counter (int): Counter for total requests

            Returns:
                    availability (bool): Availability percentage

    '''
    # Round floating-point availability percentages to the nearest whole percentage
    return round((outcome_up_counter / total_req_counter) * 100)
