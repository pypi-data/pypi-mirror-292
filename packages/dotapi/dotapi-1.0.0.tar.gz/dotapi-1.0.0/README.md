# DotAPI Python API library

The DotAPI Python library provides convenient access to the DotAPI REST API from any Python 3.7+
application.

## Installation

```sh
pip install dotapi
```

## Usage

```python
from dotapi import OpenAI

client = OpenAI(
    api_key="My DotAPI Key",  # defaults to os.environ.get("DOTROUTER_API_KEY")
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ]
    # No need to pass model, dotapi will decide the best model for your query!
)
```