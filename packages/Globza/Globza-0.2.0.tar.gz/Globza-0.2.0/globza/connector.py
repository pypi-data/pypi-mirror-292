# connector.py

import requests
import uuid


class API:
    """
    API class to interact with the cloud service for function registration and invocation.
    """
    def __init__(self, base_url='https://apiwwf-production.up.railway.app'):
        """
        Initialize with the base URL of the cloud service.
        """
        self.base_url = base_url

    def __getattr__(self, function_name):
        """
        Dynamically create a method corresponding to the called function name.
        """
        def method(*args, **kwargs):
            request_id = uuid.uuid4().hex  # Generation a unique UUID for each request
            url = f"{self.base_url}/{function_name}"

            # Extracting types and removing them from kwargs before sending
            types = kwargs.pop('types', {})

            # Convert types to strings to send in the request
            types_str = {key: value.__name__ for key, value in types.items()}

            # Convert all kwargs values ​​to strings if they are not serializable
            for key, value in kwargs.items():
                if not isinstance(value, (str, int, float, bool, type(None))):
                    kwargs[key] = str(value)  # Converting Non-JSON Serializable Objects to Strings

            payload = {'request_id': request_id, 'args': args, 'kwargs': kwargs, 'types': types_str}
            print(f"Payload being sent: {payload}")  # Logging payload before sending
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                data = result.get('data', None)  # Safe data receipt

                # Convert a string to the desired type based on the type name
                return_type = result.get('metadata', {}).get('return_type', 'json')
                if isinstance(data, str) and return_type in types:
                    # Applying the appropriate transformation using dynamic type creation
                    return types[return_type](data)

                return result['data']  # By default return as is

            except requests.exceptions.HTTPError as e:
                return {'error': 'HTTP error', 'message': str(e)}
            except requests.exceptions.RequestException as e:
                return {'error': 'Request error', 'message': str(e)}
            except ValueError as e:
                return {'error': 'Decode error', 'message': str(e)}

        return method

    def to_register_function(self, id, function_url, metadata=None):
        """
        Register a function with the cloud service.
        """
        url = f"{self.base_url}/register_function"
        payload = {'id': id, 'function_url': function_url, 'metadata': metadata or {}}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def to_call_function(self, id, *args, **kwargs):
        """
        Call a registered function by its identifier with provided arguments.
        """
        return self.__getattr__(id)(*args, **kwargs)


api = API()