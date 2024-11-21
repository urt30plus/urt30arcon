# Quake3 Async RCON Client


## Requirements

- Game: [Urban Terror 4.3.4](https://www.urbanterror.info/)
- Python: 3.12+

## Usage

```python
import asyncio
import os

from urt30arcon import AsyncRconClient


async def async_main() -> None:
    rcon_host = os.getenv("RCON_HOST", "127.0.0.1")
    rcon_port = int(os.getenv("RCON_PORT", "27960"))
    rcon_pass = os.environ["RCON_PASS"]

    client = await AsyncRconClient.create_client(
        host=rcon_host,
        port=rcon_port,
        password=rcon_pass,
    )

    await client.bigtext("hello world")
    game = await client.game_info()
    if game.players:
        first_player = game.players[0]
        await client.slap(slot=first_player.slot)


if __name__ == '__main__':
    asyncio.run(async_main())
```
