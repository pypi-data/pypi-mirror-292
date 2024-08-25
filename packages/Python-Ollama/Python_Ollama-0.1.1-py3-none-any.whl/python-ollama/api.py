import requests
import json

class OllamaAPI:
    """
    A Python client for interacting with the Ollama API.

    This class provides easy-to-use methods to manage models, generate text,
    create embeddings, and perform other actions available through the Ollama API.

    Example Usage:
        >>> ollama = OllamaAPI()
        >>> models = ollama.get_models()
        >>> print(models)  # Output: List of available models
        >>> response = ollama.generate(model="llama2", prompt="Hello, world!")
        >>> print(response)  # Output: Generated text from llama2
        >>> ollama.model.create(name="my_model", path="/path/to/my/model") # Create a new model
    """

    def __init__(self, base_url="http://localhost:11434"):
        """
        Initializes the OllamaAPI client.

        Args:
            base_url (str, optional): The base URL of the Ollama API server. 
                                       Defaults to "http://localhost:11434".
        """
        self.base_url = base_url
        self.model = self.Model(self.base_url)
        self.generate = self.Generate(self.base_url)

    def _make_request(self, method, endpoint, json_data=None, stream=False):
        """Helper function to make HTTP requests to the Ollama API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        response = requests.request(method, url, headers=headers, json=json_data, stream=stream)

        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

        if stream:
            return response.iter_content(chunk_size=1024)  # For large responses
        else:
            return response.json()

    # --- Model Management ---
    class Model:
        """
        Provides methods for managing Ollama models.
        """

        def __init__(self, base_url):
            self.base_url = base_url

        def create(self, name, modelfile=None, path=None, **kwargs):
            """
            Creates a new Ollama model.

            Args:
                name (str): The name for the new model.
                modelfile (str, optional): The content of the Modelfile.
                path (str, optional): The path to the Modelfile on the server. 
                **kwargs: Additional parameters for model creation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary. 
            """
            return self._make_request("POST", "/api/create", 
                                      json_data={"name": name, "modelfile": modelfile, "path": path, **kwargs})

        def delete(self, name):
            """
            Deletes an Ollama model.

            Args:
                name (str): The name of the model to delete.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("DELETE", "/api/delete", json_data={"name": name})

        def pull(self, name, **kwargs):
            """
            Downloads (pulls) an Ollama model.

            Args:
                name (str): The name of the model to pull.
                **kwargs: Additional parameters for pulling the model (see Ollama API documentation).

            Returns:
                generator: A generator that yields chunks of the downloaded model data.
            """
            return self._make_request("POST", f"/api/pull", json_data={"name": name, **kwargs}, stream=True)

        def push(self, name, **kwargs):
            """
            Uploads (pushes) an Ollama model to a library.

            Args:
                name (str): The name of the model to push.
                **kwargs: Additional parameters for pushing the model (see Ollama API documentation).

            Returns:
                generator: A generator that yields chunks of the response data.
            """
            return self._make_request("POST", f"/api/push", json_data={"name": name, **kwargs}, stream=True)

        def get(self, name):
            """
            Retrieves information about a specific Ollama model.

            Args:
                name (str): The name of the model.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("GET", f"/api/models/{name}")

        def show(self, name, **kwargs):
            """
            Shows detailed information about a model, including its Modelfile, template, 
            parameters, license, and system prompt.

            Args:
                name (str): The name of the model.
                **kwargs: Additional parameters for showing model information (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("POST", "/api/show", json_data={"name": name, **kwargs})

        def copy(self, source, destination):
            """
            Creates a copy of an existing Ollama model.

            Args:
                source (str): The name of the model to copy.
                destination (str): The name for the new copied model.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("POST", "/api/copy", json_data={"source": source, "destination": destination})

        def running(self):
            """
            Lists all Ollama models currently loaded in memory.

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("GET", "/api/ps")

    # --- Text & Chat Completion ---
    class Generate:
        """
        Provides methods for text and chat completion using Ollama models.
        """

        def __init__(self, base_url):
            self.base_url = base_url

        def response(self, model, prompt, **kwargs):
            """
            Generates text from a prompt (alias for `ollama.generate()`).

            Args:
                model (str): The name of the model to use.
                prompt (str): The prompt to generate text from.
                **kwargs: Additional parameters for text generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("POST", "/api/generate", json_data={"model": model, "prompt": prompt, **kwargs})

        def completion(self, model, prompt, **kwargs):
            """
            Generates text from a prompt (alias for `ollama.generate()`).

            Args:
                model (str): The name of the model to use.
                prompt (str): The prompt to generate text from.
                **kwargs: Additional parameters for text generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("POST", "/api/generate", json_data={"model": model, "prompt": prompt, **kwargs})

        def embedding(self, model, input_data, **kwargs):
            """
            Generates embeddings from a model.

            Args:
                model (str): The name of the model to use.
                input_data (str or list): The text to generate embeddings for. 
                                          Can be a string or a list of strings.
                **kwargs: Additional parameters for embedding generation (see Ollama API documentation).

            Returns:
                dict: The API response as a JSON dictionary.
            """
            return self._make_request("POST", "/api/embed", json_data={"model": model, "input": input_data, **kwargs})

    # --- Other Ollama API Methods ---
    def get_models(self):
        """
        Gets a list of available models on the Ollama server.

        Returns:
            dict: The API response as a JSON dictionary.
        """
        return self.get("/api/tags")

    def check_blob_exists(self, digest):
        """
        Checks if a file blob (used for FROM/ADAPTER fields in Modelfiles) 
        exists on the server. 

        Args:
            digest (str): The SHA256 digest of the blob.

        Returns:
            requests.Response: The HEAD response from the Ollama server. 
                               A 200 status code means the blob exists.
        """
        return self.head(f"/api/blobs/{digest}")

    def create_blob(self, digest, file_path):
        """
        Uploads a file as a blob to the Ollama server. This can be used
        to provide model files or adapter files when creating models. 

        Args:
            digest (str): The expected SHA256 digest of the file.
            file_path (str): The path to the file to be uploaded.

        Returns:
            str: The server's response (usually indicates the file path on the server).
        """
        with open(file_path, "rb") as f:
            file_data = f.read()
        response = requests.post(f"{self.base_url}/api/blobs/{digest}", data=file_data)
        response.raise_for_status() 
        return response.text
