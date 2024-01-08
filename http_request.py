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
    * IsValidJsonFormat - function for JSON formatted string validation
    * SetHttpReqData - prepare HTTP request data for sending on server
"""
import time
import requests
import json
import sys

# Global constants
DEFAULT_HTTP_METHOD = 'GET' # Default HTTP method
DEFAULT_HTTP_HEADERS = None # Default HTTP request header
DEFAULT_HTTP_BODY = None # Default HTTP request body

UP_START_CODE = 200 # lower end of HTTP status code for UP outcome
UP_END_CODE = 299 # upper end of HTTP status code for UP outcome
UP_MAX_LATENCY_MS = 500 # HTTP request latency from server response in millisconds
HTTP_REQ_TIMEOUT_S = 0.5 # HTTP request timeout in seconds (for optimal solution this should be equivalent to UP_MAX_LATENCY_MS)

CYCLE_DELAY = 15 # Cycle delay in seconds

# Map request methods with belonging HTTP methods
REQUEST_FUNCTIONS = {
    "POST": requests.post,
    "PUT": requests.put,
    "DELETE": requests.delete,
    "GET": requests.get,
    "PATCH": requests.patch,
    "HEAD": requests.head,
    "OPTIONS": requests.options
}

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


def SetUrlDomainGroups(data_from_yaml: dict, timeout: float = HTTP_REQ_TIMEOUT_S):
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
        # Check for required endpoint elements
        if "url" in endpoint and "name" in endpoint:
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
                    data: list of all relevant data for single endpoint request which belongs to url domain
                    total_requests: counter of total HTTP requests sent to url domain
                    total_outcome_up: counter of total UP outcomes for all HTTP requests sent to url domain 
                """
                urls[url_domain] = {"data": [], "total_requests" : 0, "total_outcome_up" : 0}
            """
            Endpoint request data:
                key -> req_function
                value -> request function

                key -> url
                value -> url argument for request function

                key -> params
                value -> paramteres for request function
            """
            endpoint_req_data = SetHttpReqData(endpoint, timeout)
            # Append data list with endpoint relevant data
            urls[url_domain]["data"].append(endpoint_req_data)

    # Return formated data
    return urls

def SendHttpRequest(endpoint: dict):
    '''
    Send HTTP request to endpoint

            Parameters:
                    endpoint (dict): Endpoint relevant data

            Returns:
                    outcome (bool): Outcome for HTTP request

    '''
    try:
        # Set HTTP request function, url and parameters for endpoint
        request_func = endpoint["req_function"]
        url = endpoint["url"]
        params = endpoint["params"]
        # Send HTTP request
        r = request_func(url, **params)
    # Handle exception for sent HTTP request
    except Exception as e:
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

def IsValidJsonFormat(jsonData: str):
    '''
    Validate if given string is JSON formatted

            Parameters:
                    jsonData (str): string for validation

            Returns:
                    status (bool): Validity status

    '''
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

def SetHttpReqData(endpoint: dict, timeout: float):
    '''
    Preparing data for handling HTTP request

            Parameters:
                    endpoint (dict): endpoint data from config file
                    timeout (float): timeout for HTTP request

            Returns:
                    object (dict): Relevant HTTP request data

    '''
    # Set default value for each relevant parameter for HTTP request
    method = DEFAULT_HTTP_METHOD if "method" not in endpoint else endpoint["method"]
    headers = DEFAULT_HTTP_HEADERS if "headers" not in endpoint else endpoint["headers"]
    body = endpoint["body"] if "body" in endpoint and IsValidJsonFormat(endpoint["body"]) else DEFAULT_HTTP_BODY
    # Set basic parameter for every type of HTTP request
    params = {"timeout": timeout}
    # Add additional parameters if needed
    if body and method in ("POST", "PUT", "PATCH"):
        params["data"] = body
    if headers:
        params["headers"] = headers
    # Return formatted HTTP request relevant data
    return {"req_function" : REQUEST_FUNCTIONS[method], "url": endpoint["url"], "params" : params}