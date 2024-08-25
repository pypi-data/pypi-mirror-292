from setuptools import setup, find_packages

setup(
    name="Python-Ollama",
    version="0.2.2",
    description="Python client for the Ollama API",
    author="Kaede Dev Kento Hinode",
    author_email="cleaverdeath@gmail.com",
    url="https://github.com/DarsheeeGamer/Python-Ollama/",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
