# nusuGraph

An asynchronous and simplified wrapper for the Telegraph API.

## Installation

```bash
pip install -U nusugraph
```

## Usage

```python
import asyncio
from nusugraph import Telegraph


async def main():
    graph = Telegraph(
        token=None,  # if no token was passed, then an anonymous account will be created
        tokenList=None,  # list of tokens to be used in a cycle
        timeout=10,  # timeout for httpx.AsyncClient
    )

    # Create a Page
    text = "Hello, world!"

    # Account will be created if no token was passed
    response = await graph.createPage(
        author="Nusab Taha", htmlContent="<b>Hello</b>", title="Just Saying Hello"
    )
    url = response["url"]
    print(url)  # https://telegra.ph/Just-Saying-Hello-12-28-4

    # Upload Media from local file
    imagePath = "assets/sample.jpg"
    url = await graph.uploadMediaFromFile(imagePath)
    print(url)  # https://telegra.ph/file/daf9c776a1c25264321cd.jpg

    # Upload Media from it's bytes content
    with open(imagePath, "rb") as file:
        imageBytes = file.read()

    url = await graph.uploadMediaFromBytes(content=imageBytes, fileType="image/jpeg")
    print(url)  # https://telegra.ph/file/3406d7261c8c62869ab91.jpg


if __name__ == "__main__":
    asyncio.run(main())
```

## WHY?

I needed a simple and asynchronous wrapper for the Telegraph API, with the ability to use multiple tokens in a cycle. That's the reason.
