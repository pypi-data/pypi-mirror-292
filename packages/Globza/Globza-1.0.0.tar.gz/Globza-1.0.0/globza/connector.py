# connector.py (for globza)
# Version 1.0.0
# author: © Sergei Sychev, 2024 , see also LICENSE.txt

"""
This module provides the API class to interact with a cloud-based function service.
The class dynamically handles function calls to remote services by generating methods on-the-fly,
converting argument types as needed, and handling HTTP requests and responses. It also allows
for registering new functions with the service.

Classes:
    API: A class to handle function registration and invocation for cloud-based services.
"""

import requests
import uuid


class API:
    """
    A class to interact with the cloud service for function registration and invocation.

    This class handles dynamic creation of methods corresponding to registered functions
    and manages HTTP requests to invoke these functions. It also handles converting the types
    of function arguments and results using specified metadata.

    Attributes:
        base_url (str): The base URL of the cloud service.
    """

    def __init__(self, base_url='https://apiwwf-production.up.railway.app'):
        """
        Initializes the API class with a base URL for the cloud service.

        Parameters:
            base_url (str): The base URL of the cloud service. Defaults to a specific production URL.
        """
        self.base_url = base_url

    def __getattr__(self, function_name):
        """
        Dynamically creates a method corresponding to the called function name.

        This method allows the API class to handle arbitrary function calls by generating
        a callable method that sends a request to the corresponding endpoint on the cloud service.

        Parameters:
            function_name (str): The name of the function being called.

        Returns:
            method (function): A method that, when called, sends a request to the cloud service.
        """

        def method(*args, **kwargs):
            """
            Sends a request to invoke a remote function with the provided arguments.

            This method constructs a request with the function's arguments, sends it to the cloud service,
            handles the response, and performs type conversion if necessary.

            Parameters:
                *args: Positional arguments for the function call.
                **kwargs: Keyword arguments for the function call, including a 'types' argument to specify type conversion.

            Returns:
                dict: The response data from the function call, possibly after type conversion.
            """
            # Generate a unique request ID
            request_id = uuid.uuid4().hex
            # Construct the URL for the function
            url = f"{self.base_url}/{function_name}"

            # Extract 'types' for type conversion
            types = kwargs.pop('types', {})

            # Convert non-serializable keyword arguments to strings
            for key, value in kwargs.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    kwargs[key] = str(value)

            # Prepare the payload for the request
            payload = {'request_id': request_id, 'args': args, 'kwargs': kwargs,
                       'types': {key: value.__name__ for key, value in types.items()}}

            try:
                # Send a POST request to the cloud service
                response = requests.post(url, json=payload)
                response.raise_for_status()  # Raise an error for bad responses
                result = response.json()
                data = result.get('data', None)

                # Convert the response data using specified types
                if data and isinstance(data, dict):  # Check if data is a dictionary
                    for key, type_func in types.items():
                        if key in data:
                            data[key] = type_func(data[key])

                return data

            except requests.exceptions.HTTPError as e:
                return {'error': 'HTTP error', 'message': str(e)}
            except requests.exceptions.RequestException as e:
                return {'error': 'Request error', 'message': str(e)}
            except ValueError as e:
                return {'error': 'Decode error', 'message': str(e)}

        return method

    def to_register_function(self, id, function_url, metadata=None):
        """
        Registers a function with the cloud service.

        This method sends a request to register a new function, identified by a unique ID,
        with its corresponding URL and metadata, to the cloud service.

        Parameters:
            id (str): The unique identifier for the function.
            function_url (str): The URL where the function is hosted.
            metadata (dict, optional): Additional metadata for the function, such as HTTP method or return type.

        Returns:
            dict: The response from the cloud service confirming the registration.
        """
        url = f"{self.base_url}/register_function"
        payload = {'id': id, 'function_url': function_url, 'metadata': metadata or {}}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def to_call_function(self, id, *args, **kwargs):
        """
        Calls a registered function by its identifier with provided arguments.

        This method allows for direct invocation of a registered function using its ID,
        passing any required positional and keyword arguments.

        Parameters:
            id (str): The unique identifier of the function to be called.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            dict: The response data from the function call.
        """
        return self.__getattr__(id)(*args, **kwargs)


api = API()
