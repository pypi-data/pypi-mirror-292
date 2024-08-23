# Saldor

Saldor is a Python client library for interacting with the Saldor.com API. It
allows developers to easily integrate Saldor's services into their Python
applications.

## Examples

### Using the python library

```
pip install saldor
```

Writing a basic app that uses the client:

```
import os

import saldor

client = saldor.SaldorClient(api_key=os.getenv("SALDOR_API_KEY"))


documents = client.scrape_url(
    url="URL",
    params={},
)
# Create a directory called 'results' if it doesn't exist
os.makedirs("results", exist_ok=True)

# Iterate through the documents and save each as a markdown file
for i, document in enumerate(documents["data"]):
    file_path = os.path.join("results", f"{i}.md")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(document)
```

### Using curl

```
curl -X POST "https://api.saldor.com/scrape" \
     -H "x-api-key: API-KEY" \
     -H "Content-Type: application/json" \
     -d '{"url": "URL", "params": {}}'
```



