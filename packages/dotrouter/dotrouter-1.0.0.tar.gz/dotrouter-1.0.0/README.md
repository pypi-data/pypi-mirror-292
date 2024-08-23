# Dotrouter Python API library

The Dotrouter Python library provides convenient access to the Dotrouter REST API from any Python 3.7+
application.

## Installation

```sh
pip install dotrouter
```

## Usage

```python
from dotrouter import OpenAI

client = OpenAI(
    api_key="My Dotrouter Key",  # defaults to os.environ.get("DOTROUTER_API_KEY")
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ]
    # No need to pass model, dotrouter will decide the best model for your query!
)
```