# NOVA Machine to Machine Client

The NOVA client allows to you interact with the NOVA Machine to Machine API to create chat completions and manage sessions.

## Installation

```bash
pip install nova-client
```
## Usage

```python
from nova_client import NOVAClient

async def main():
    client = NOVAClient(api_key="...")

    session = await client.client_sessions.create_session(bot_id="bot-...")
    token = session.session_token
    # The session token can be shared with an end device (e.g. website, mobile app).

    # To create completions directly:
    stream = session.send_message("Tell me a joke!")

    async for event in stream:
        print("event:", event)
```

### Cancellation

The NOVA Api supports interruptions of completions. To cancel a completion, you can cancel the asyncio task that is running the completion.

```python
import asyncio
from nova_client import NOVAClient

async def run_completion():
    client = NOVAClient(api_key="...")
    session = await client.client_sessions.create_session(bot_id="bot-...")

    stream = session.send_message("Tell me a joke!")

    async for event in stream:
        print("event:", event)


async def main():
    task = asyncio.create_task(run_completion())
    await asyncio.sleep(5)
    task.cancel()
    await task
```
