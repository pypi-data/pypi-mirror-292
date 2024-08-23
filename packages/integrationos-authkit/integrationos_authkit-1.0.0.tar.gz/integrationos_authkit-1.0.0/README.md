# IntegrationOS AuthKit SDK for Python

Secure token generation for [IntegrationOS AuthKit](https://docs.integrationos.com/docs/authkit) using [PyPI](https://pypi.org/).

## Installation

You can install the IntegrationOS AuthKit SDK using pip:

```
pip install integrationos-authkit
```

## Usage

Here's a quick example of how to use the SDK:

```python
from integrationos import AuthKit

@app.route('/authkit-token', methods=['POST'])
def create_authkit_token():
    payload = {
        "group": "meaningful-id", # a meaningful identifier (i.e., organizationId)
        "label": "Friendly Label", # a human-friendly label (i.e., organizationName)
    }

    embed_token = AuthKit("sk_live_12345")
    response = embed_token.create(payload)

    return response
```

You'll want to switch out the API Key for your own, which will later tell your frontend which integrations you'd like to make available to your users.

You'll also want to populate the `Group` and `Label` fields depending on how you want to organize and query your users' connected accounts. The Group is especially important as it's used to generate the unique [Connection Key](https://docs.integrationos.com/docs/setup) for the user once they successfully connect an account.

## Full Documentation

Please refer to the official [IntegrationOS AuthKit](https://docs.integrationos.com/docs/authkit) docs for a more holistic understanding of IntegrationOS AuthKit.