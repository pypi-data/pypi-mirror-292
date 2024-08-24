# Async Python Client to The RTEX API Server

## Installation

```bash
pip install rtex
```

## Usage

The API surface of Rtex is spartan so this is basically the whole thing.

```python
import asyncio

from rtex.client import AsyncRtexClient

async def amain():
  async with AsyncRtexClient() as rtex:
    res = rtex.create_render("\(x^2 + x - 1\)")

    if res.status == "success":
      with open("equation.png") as output_fd:
        await res.save_render(
          res.filename,
          output_fd
        )

def main():
  asyncio.run(amain())

if __name__ == "__main__":
  main()
```

## No Thoughts, Just Render

```python
async def amain():
  async with AsyncRtexClient() as rtex:
    buf = await rtex.render_math("e^x + 1")

    # `buf` now contains the bytes of the PNG
```

## Do I look like I know what a Jay-Peg is?

```python
async def amain():
  async with AsyncRtexClient() as rtex:
    # The render methods accept a format parameter.
    # Supported values are "png", "jpg" and "pdf"
    buf = await rtex.render_math("e^x + 1", format="jpg")
```

## Self-Hoster

Set the environment variable `RTEX_API_HOST` or do the following.

```python

async def amain():
  async with AsyncRtexClient(api_host="https://myserver.ru") as rtex:
    buf = await rtex.render_math("e^x + 1")
```


## I Can Tell By The Pixels

`quality` in Rtex speak is an abstract notion of compression for the given
format where `100` is the least compressed and `0` is the most. At the time of
writing the default is `85`.

`density` in Rtex speak is how much to sample the rendered PDF when generating
an image. This has no effect on the `"pdf"` format. At the time of writing the
default is `200`.

```python

async def amain():
  async with AsyncRtexClient(api_host="https://myserver.ru") as rtex:
    needs_more_jpeg = await rtex.render_math(
      "e^x + 1",
      density=50,
      quality=1
    )
```

