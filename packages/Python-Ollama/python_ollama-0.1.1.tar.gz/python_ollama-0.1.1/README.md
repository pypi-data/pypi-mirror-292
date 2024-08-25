# Python-Ollama: Unleashing the Power of Ollama in Your Python Projects

[![PyPI version](https://badge.fury.io/py/python-ollama.svg)](https://badge.fury.io/py/python-ollama)

`python-ollama` is your comprehensive and intuitive Python client for the Ollama API. This package gives you the tools to harness the power of Ollama's large language models directly within your Python applications. With its user-friendly design, `python-ollama` simplifies model management, text generation, chat interactions, embedding creation, and other advanced Ollama functionalities.

## Key Features

- **Full API Coverage:** Interact seamlessly with every Ollama API endpoint, granting you granular control over your Ollama server and models.
- **Pythonic Design:** Enjoy a clean, intuitive, and Pythonic API structure that mirrors the Ollama API, making it easy to learn and use.
- **Simplified Requests:** Abstracted HTTP request handling and robust error management streamline your interaction with the Ollama server, ensuring a smooth and reliable experience.
- **Comprehensive Documentation:** Each method and class is meticulously documented with clear explanations, parameter descriptions, return types, and illustrative examples to guide you through every aspect of the API.
- **Extensible & Future-Proof:**  Built with flexibility in mind, `python-ollama` is designed to easily accommodate future Ollama API updates and extensions, ensuring compatibility and long-term value. 

## Installation

Get started with `python-ollama` by installing it via pip:

```bash
pip install python-ollama
```

## Usage

### 1. Import and Initialize

Begin by importing the `OllamaAPI` class and creating an instance:

```python
from python_ollama import OllamaAPI

# Initialize the API client, optionally specifying a custom base URL
ollama = OllamaAPI()  # Defaults to http://localhost:11434
# or
ollama = OllamaAPI(base_url="http://your-ollama-server:port")  # Your custom Ollama server 
```

### 2. Master Model Management with `ollama.model`

`python-ollama` provides a powerful nested class, `ollama.model`, to give you full control over managing Ollama models. 

#### 2.1. Create New Models: `ollama.model.create()`

The `create` method allows you to create new models on your Ollama server. You can either specify a path to a Modelfile on the server or provide the Modelfile content directly:

```python
# Create a model from a Modelfile on the server
ollama.model.create(name="my-gpt2-model", path="/path/to/my/gpt2/modelfile.yaml")

# Create a model by providing the Modelfile content
modelfile_content = """
FROM llama2
SYSTEM You are a friendly and helpful assistant.
"""
ollama.model.create(name="my-assistant", modelfile=modelfile_content)
```

**Parameters:**

- `name (str)`: **Required**. The desired name for your new model. Choose a descriptive name that reflects the model's purpose. 
- `modelfile (str, optional)`: The contents of the Modelfile. If you are providing the file content, ensure it's a valid YAML-formatted Ollama Modelfile. 
- `path (str, optional)`: The file path to an existing Modelfile on your Ollama server. Make sure the path is correct and that the file is accessible to Ollama.
- `**kwargs`: Additional parameters for model creation. Refer to the Ollama API documentation for a complete list and details. 

**Example Use Cases:**

- Create specialized models tailored to specific tasks, such as code generation, question answering, or summarization, by customizing the Modelfile content. 
- Experiment with different base models and parameters to fine-tune model performance for your applications.

#### 2.2. Delete Existing Models: `ollama.model.delete()`

Remove models that you no longer need from your Ollama server to free up space and keep your model library organized:

```python
ollama.model.delete(name="my-old-model")
```

**Parameters:**

- `name (str)`: **Required**. The name of the model you want to delete.

**Example Use Cases:**

- Delete outdated or unused models to maintain a clean and efficient model repository.
- Remove experimental models after completing your evaluations.

#### 2.3. Download (Pull) Models: `ollama.model.pull()`

Download models from the Ollama library or remote repositories to your Ollama server. The `pull` method handles the download process and allows you to process the downloaded model data in chunks:

```python
# Download the "llama2" model and save it to a file
for chunk in ollama.model.pull(name="llama2"):
    with open("llama2.bin", "wb") as f:
        f.write(chunk)
```

**Parameters:**

- `name (str)`: **Required**. The name of the model to download (pull).
- `**kwargs`: Additional parameters to customize the pull process, such as `insecure` (for local development/testing). Consult the Ollama documentation for a complete list. 

**Example Use Cases:**

- Download pre-trained models from the Ollama library to experiment with or use in your applications.
- Obtain updated versions of models to leverage the latest improvements and fixes.

#### 2.4. Upload (Push) Models: `ollama.model.push()`

Share your custom models with the Ollama community or upload them to a private model library:

```python
for chunk in ollama.model.push(name="my-namespace/my-model:v1"):
    print(chunk.decode(), end="")  # Print progress updates during the upload
```

**Parameters:**

- `name (str)`: **Required**. The name of the model to push. Include the namespace and tag if relevant (e.g., "my-namespace/my-model:v1"). 
- `**kwargs`: Additional parameters for model pushing, such as `insecure` for local development. Refer to the Ollama documentation for details. 

**Example Use Cases:**

- Share your fine-tuned or custom-trained models with others.
- Back up your models to a remote repository. 

#### 2.5. Retrieve Model Information: `ollama.model.get()`

Get essential information about a model, such as its size, digest, and basic details:

```python
info = ollama.model.get(name="llama2") 
print(info) 
```

**Parameters:**

- `name (str)`: **Required**. The name of the model.

**Example Use Cases:**

- Check the details of a model before using it.
- Verify the size of a model to ensure it fits within your system's resources. 

#### 2.6. Show Detailed Model Information: `ollama.model.show()`

Retrieve comprehensive information about a model, including its Modelfile, template, parameters, license, system prompt, and other relevant details:

```python
# Get detailed information about the "mistral" model, including full verbose output
details = ollama.model.show(name="mistral", verbose=True) 
print(details) 
```

**Parameters:**

- `name (str)`: **Required**. The name of the model.
- `verbose (bool, optional)`: Set to `True` to retrieve full data for verbose response fields. Defaults to `False`.

**Example Use Cases:**

- Inspect the Modelfile and template of a model to understand its configuration.
- Review the license information before using a model in your applications. 

#### 2.7. Duplicate Existing Models: `ollama.model.copy()`

Create a copy of an existing model, allowing you to experiment with model modifications or create backups:

```python
# Create a copy of "llama2" named "llama2-backup"
ollama.model.copy(source="llama2", destination="llama2-backup")
```

**Parameters:**

- `source (str)`: **Required**. The name of the existing model you want to copy.
- `destination (str)`: **Required**. The name you want to give to the new copied model. 

**Example Use Cases:**

- Experiment with modifications to a model's parameters or Modelfile without affecting the original model.
- Create backups of important models to safeguard against accidental deletion or data loss.

#### 2.8. List Running Models: `ollama.model.running()`

Get a list of all models currently loaded and running in memory on your Ollama server:

```python
running_models = ollama.model.running()
print(running_models)
```

**Example Use Cases:**

- Monitor the models currently in use on your Ollama server.
- Check for resource usage by loaded models. 

### 3. Text Generation and Chat with `ollama.generate`

The `ollama.generate` nested class gives you the power to generate text and engage in multi-turn chat conversations using Ollama's language models. 

#### 3.1. Generate Text: `ollama.generate()`, `ollama.generate.response()`, `ollama.generate.completion()`

Use these methods to generate text from a given prompt:

```python
# Generate text using the "llama2" model
response = ollama.generate(model="llama2", prompt="Tell me a fun fact about space.")
print(response)

# Aliases for `ollama.generate()`:
response = ollama.generate.response(model="llama2", prompt="Translate 'hello' to Spanish.")
print(response)

response = ollama.generate.completion(model="llama2", prompt="Complete this sentence: The quick brown fox...")
print(response)
```

**Parameters:**

- `model (str)`: **Required**. The name of the model to use for text generation.
- `prompt (str)`: **Required**. The text prompt that the model should use as a starting point for generating text.
- `**kwargs`: Additional parameters to customize text generation, including:
    - `temperature (float)`: Controls the randomness of the generated text (higher values result in more random output).
    - `top_k (int)`:  Limits the number of possible next words considered by the model.
    - `stop (list)`: Specifies stop sequences that will cause the model to stop generating text.

Refer to the Ollama API documentation for a comprehensive list of available parameters.

**Example Use Cases:**

- Creative writing: Generate stories, poems, scripts, and other creative text formats.
- Code generation: Ask the model to write code in specific programming languages.
- Question answering: Get answers to factual or open-ended questions.
- Summarization: Condense large amounts of text into concise summaries. 

#### 3.2. Engage in Multi-Turn Conversations: `ollama.chat()`

Create dynamic and interactive chat experiences with Ollama's chat-capable models:

```python
# Start a conversation with the "llama2" model
conversation = [
    {"role": "system", "content": "You are a friendly AI assistant."},
    {"role": "user", "content": "What is the capital of Australia?"}
]
response = ollama.chat(model="llama2", messages=conversation)
print(response)
```

**Parameters:**

- `model (str)`: **Required**. The name of the chat-capable model to use.
- `messages (list)`: **Required**. A list of message dictionaries representing the conversation history. Each dictionary should have the following keys:
    - `role (str)`:  The role of the sender ("system", "user", or "assistant").
    - `content (str)`: The text content of the message. 
- `**kwargs`: Additional parameters to control the chat interaction, including:
    - `stream (bool)`:  Set to `True` to receive responses in a streaming fashion (for real-time updates). Defaults to `False`.
    - `tools (list)`: (Advanced) Provide a list of tool definitions to enable the model to interact with external APIs or tools. See the Ollama documentation for details.

**Example Use Cases:**

- Build engaging chatbots that can hold natural conversations.
- Create interactive storytelling experiences. 
- Develop AI-powered assistants to help users with tasks or provide information. 

### 4. Generate Embeddings: `ollama.generate.embedding()`

Create vector representations of text, useful for tasks like semantic similarity, clustering, and search:

```python
# Generate embeddings for a list of sentences
embeddings = ollama.generate.embedding(model="all-mpnet-base-v2", input_data=["This is a sentence.", "This is another sentence."])
print(embeddings) 
```

**Parameters:**

- `model (str)`: **Required**. The name of the embedding model to use. 
- `input_data (str or list)`: **Required**. The input text. You can provide a single string or a list of strings.
- `**kwargs`: Additional parameters (refer to Ollama documentation for advanced options).

**Example Use Cases:**

- Semantic search: Find documents or information related to a given query based on meaning, not just keywords. 
- Recommendation systems:  Suggest items or content based on the similarity of embeddings.
- Clustering: Group similar pieces of text together based on their embeddings.

### 5. Advanced Ollama API Features

#### 5.1. List Available Models: `ollama.get_models()`

Retrieve a list of all models available on your Ollama server:

```python
all_models = ollama.get_models()
print(all_models) 
```

#### 5.2. Check for Existing Blobs: `ollama.check_blob_exists()`

Verify if a particular file blob, often used for model or adapter files, is present on the server:

```python
# Check if a blob with the given SHA256 digest exists
blob_exists = ollama.check_blob_exists(digest="sha256:your_blob_digest")
if blob_exists.status_code == 200:
    print("The blob exists on the server!")
```

**Parameters:**

- `digest (str)`: **Required**. The SHA256 digest of the blob to check.

#### 5.3. Upload Files as Blobs: `ollama.create_blob()`

Upload a file to the Ollama server as a blob. This is useful for providing model files or adapter files when creating new models:

```python
ollama.create_blob(digest="sha256:your_blob_digest", file_path="/path/to/your/model.bin")
```

**Parameters:**

- `digest (str)`: **Required**. The expected SHA256 digest of the file. 
- `file_path (str)`: **Required**. The path to the file on your local system that you want to upload.

## Contributing

We encourage contributions to make `python-ollama` even better! Here's how you can get involved:

* **Report Issues:** Found a bug, have a feature request, or want to suggest an improvement? Please open an issue on the [GitHub repository](https://github.com/DarsheeeGamer/Python-Ollama).
* **Submit Pull Requests:** Contribute bug fixes, new features, enhancements, or optimizations. Make sure your code adheres to the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
