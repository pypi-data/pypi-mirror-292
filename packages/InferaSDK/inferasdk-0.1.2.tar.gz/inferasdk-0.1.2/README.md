# InferaSDK

InferaSDK is a Python package that provides a fast, flexible, and intuitive interface for interacting with the Infera API. It aims to simplify the process of submitting jobs, processing multiple requests concurrently, and retrieving results efficiently from various language models.

## Table of Contents
- [Main Features](#main-features)
- [Where to get it](#where-to-get-it)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Getting Help](#getting-help)


## Main Features
Here are just a few of the things that InferaSDK does well:

- Asynchronous API interactions for efficient processing
- Concurrent job submission and handling
- Easy integration with multiple language models
- Automatic job status polling and result retrieval
- Flexible parameter configuration for each job (e.g., max_output, temperature)
- Timeout handling to manage long-running requests

## Where to get it
The source code is currently hosted on GitHub at: https://github.com/inferanetwork/InferaSDK

Binary installers for the latest released version are available at the Python Package Index (PyPI).

## Installation:

Install InferaSDK using pip:

```
pip install InferaSDK
```

For the latest development version, you can install directly from the Github repository:

## Usage
Here's a quick example of how to use InferaSDK:

```
import asyncio
import aiohttp
from inferaSDK import InferaSDK

async def main():
    api_key = "your_api_key_here"  # Replace with your actual API key
    sdk = InferaSDK(api_key)
    
    model = "llama3.1:latest"
    messages = [{"role": "user", "content": "What is the capital of France?"}]
    max_output = 100
    temperature = 0.7

    async with aiohttp.ClientSession() as session:
        result = await sdk.process_job(session, model, messages, max_output, temperature)
        
        print("Result:")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

This code demonstrates how to use the InferaSDK to submit a job to the Infera API and retrieve the result. Let's break it down:

1. Import statements:
   - ```asyncio```: Used for asynchronous programming in Python.
   - ```aiohttp```: An asynchronous HTTP client library.
   - ```InferaSDK```: The main class from the InferaSDK package.

2. SDK initialization:
   - Creates an instance of `InferaSDK` with your API key.

3. Job parameters:
   - `model`: Specifies the language model to use (in this case, "llama3.1:latest").
   - `messages`: A list containing a single message dictionary with the user's question.
   - `max_output`: Limits the maximum number of tokens in the response.
   - `temperature`: Controls the randomness of the output (0.7 is a balanced setting).

4. Asynchronous context manager:
   - ```async with aiohttp.ClientSession() as session```: Creates an HTTP session for making API requests.


5. Job processing:
   - ```result = await sdk.process_job(...)```: Submits the job to the API and waits for the result.


6. Result output:
   - Prints the result received from the API.


7. Script execution:
   - ```if __name__ == "__main__":```: Ensures the script runs only when executed directly.
   - ```asyncio.run(main())```: Runs the asynchronous main function.


This example showcases a simple, single-job submission to the Infera API using the InferaSDK, demonstrating how to interact with AI models asynchronously.


## Documentation
The official documentation is hosted [here](https://docs.infera.org/).

## Getting Help
You can also reach out to our support team at white@infera.org.



