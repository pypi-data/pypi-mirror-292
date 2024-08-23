import requests
from shared_kernel.interfaces.http import HttpApiClient


class RequestsHttpClient(HttpApiClient):
    """
    An implementation of the HttpApiClient interface using the requests library for synchronous HTTP requests.
    This class provides methods to interact with HTTP endpoints using common HTTP methods.

    Methods
    -------
    get(url: str, params: dict = None, headers: dict = None) -> dict:
        Sends a synchronous GET request to the specified URL.

    post(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a synchronous POST request to the specified URL.

    put(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a synchronous PUT request to the specified URL.

    delete(url: str, headers: dict = None) -> dict:
        Sends a synchronous DELETE request to the specified URL.

    patch(url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        Sends a synchronous PATCH request to the specified URL.

    head(url: str, headers: dict = None) -> dict:
        Sends a synchronous HEAD request to the specified URL.

    upload_file(url: str, file_path: str, filename: str, headers: dict = None) -> dict:
        Uploads a file synchronously to the specified URL.

    download_file(url: str, save_path: str, headers: dict = None) -> None:
        Downloads a file synchronously from the specified URL and saves it to the given path.
    """

    def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        """
        Sends a synchronous GET request to the specified URL.

        Parameters:
        - url (str): The URL to send the GET request to.
        - params (dict, optional): URL parameters to include in the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def post(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        """
        Sends a synchronous POST request to the specified URL.

        Parameters:
        - url (str): The URL to send the POST request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.post(url, data=data, json=json, headers=headers)
        return response.json()

    def put(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        """
        Sends a synchronous PUT request to the specified URL.

        Parameters:
        - url (str): The URL to send the PUT request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.put(url, data=data, json=json, headers=headers)
        return response.json()

    def delete(self, url: str, headers: dict = None) -> dict:
        """
        Sends a synchronous DELETE request to the specified URL.

        Parameters:
        - url (str): The URL to send the DELETE request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.delete(url, headers=headers)
        return response.json()

    def patch(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        """
        Sends a synchronous PATCH request to the specified URL.

        Parameters:
        - url (str): The URL to send the PATCH request to.
        - data (dict, optional): The form data to send in the body of the request.
        - json (dict, optional): A JSON object to send in the body of the request.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.patch(url, data=data, json=json, headers=headers)
        return response.json()

    def head(self, url: str, headers: dict = None) -> dict:
        """
        Sends a synchronous HEAD request to the specified URL.

        Parameters:
        - url (str): The URL to send the HEAD request to.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        response = requests.head(url, headers=headers)
        return response.json()

    def upload_file(self, url: str, file_path: str, filename: str, headers: dict = None) -> dict:
        """
        Uploads a file synchronously to the specified URL.

        Parameters:
        - url (str): The URL to send the file to.
        - file_path (str): The local path of the file to be uploaded.
        - filename (str): The name of the file to be uploaded.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - dict: The response from the server as a JSON-decoded dictionary.
        """
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={filename: file}, headers=headers)
        return response.json()

    def download_file(self, url: str, save_path: str, headers: dict = None) -> None:
        """
        Downloads a file synchronously from the specified URL and saves it to the given path.

        Parameters:
        - url (str): The URL to download the file from.
        - save_path (str): The local path where the file should be saved.
        - headers (dict, optional): HTTP headers to include in the request.

        Returns:
        - None
        """
        response = requests.get(url, headers=headers)
        with open(save_path, 'wb') as file:
            file.write(response.content)
