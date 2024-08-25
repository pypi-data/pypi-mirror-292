# python-ollama: Your Pythonic Interface to Ollama

[![PyPI version](https://badge.fury.io/py/python-ollama.svg)](https://badge.fury.io/py/python-ollama) [![Build Status](https://travis-ci.org/DarsheeeGamer/python-ollama.svg?branch=master)](https://travis-ci.org/Darsheeegamer/python-ollama) 

`python-ollama` is a powerful and intuitive Python client for the Ollama API, designed to streamline your interaction with Ollama and its language models. This package provides a Pythonic way to manage models, generate text, perform chat completions, create embeddings, and much more.

## Features

- **Full API Coverage:** Seamlessly interact with all Ollama API endpoints, giving you complete control over your Ollama server.
- **Pythonic Design:**  Enjoy a clean and intuitive API that feels natural to Python developers, with methods and classes mirroring the Ollama API structure.
- **Simplified Requests:**  Abstracted HTTP request handling with robust error management makes interacting with the API effortless.
- **Comprehensive Documentation:**  Detailed docstrings provide clear explanations, parameter descriptions, and usage examples for each method and class.
- **Extensible & Future-Proof:**  Designed for easy adaptation to future Ollama API updates and extensions.

## Installation

Install the `python-ollama` package using `pip`:

```bash
pip install python-ollama
```

## Usage

### 1. Import and Initialize

```python
from python_ollama import OllamaAPI

# Initialize the API client, optionally specifying a custom base URL
ollama = OllamaAPI()  # Defaults to http://localhost:11434
# or 
ollama = OllamaAPI(base_url="http://your-ollama-server:port")
```

### 2. Model Management (`ollama.model`)

```python
# List Available Models
models = ollama.get_models()
print(models)

# Create a New Model
ollama.model.create(name="my-awesome-model", path="/path/to/model/directory")

# Show Model Details
details = ollama.model.show(name="my-awesome-model")
print(details['modelfile'])  # Print the Modelfile content
print(details['template'])   # Print the prompt template

# Copy an Existing Model
ollama.model.copy(source="llama2", destination="my-llama2-copy")

# Delete a Model
ollama.model.delete(name="my-old-model")

# Pull a Model from the Ollama Library
for chunk in ollama.model.pull(name="mistral"):
    # Process downloaded chunks (e.g., write to a file)
    # ...

# Push a Model to a Model Library (requires proper authentication)
for chunk in ollama.model.push(name="my-namespace/my-model:latest"):
    # Process response chunks
    # ...

# Get Information About a Model
model_info = ollama.model.get(name="llama2")
print(model_info)

# List All Running Models
running_models = ollama.model.running()
print(running_models)
```

### 3. Text Generation and Chat Completion (`ollama.generate`)

```python
# Generate Text from a Prompt
response = ollama.generate(model="llama2", prompt="Write a short story about a cat.")
print(response)

# Generate a Chat Completion
messages = [
    {"role": "system", "content": "You are a friendly chatbot."},
    {"role": "user", "content": "What's your favorite color?"}
]
chat_response = ollama.chat(model="llama2", messages=messages)
print(chat_response)

# Generate Embeddings
embeddings = ollama.generate.embedding(model="all-mpnet-base-v2", input_data="This is a test sentence.")
print(embeddings)
```

### 4. Advanced Features

```python
# Check if a Blob Exists (for Model/Adapter Files)
blob_exists = ollama.check_blob_exists(digest="sha256:your_blob_digest") 
if blob_exists.status_code == 200:
    print("Blob exists on the server!")

# Create a Blob (Upload a File)
ollama.create_blob(digest="sha256:your_blob_digest", file_path="/path/to/your/file.bin")
```

## Contributing

We welcome contributions from the community! Here's how you can get involved:

* **Report Issues:**  Encountered a bug or have a feature request? Open an issue on the GitHub repository.
* **Submit Pull Requests:**  Contribute bug fixes, new features, or enhancements. Ensure your code adheres to the existing style and includes tests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
