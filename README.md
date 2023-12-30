# Quake3 Async RCON Client


## Requirements

- Game: [Urban Terror 4.3.4](https://www.urbanterror.info/)
- Python: 3.11+

## Usage

```python
import asyncio

from urt30arcon import AsyncRconClient


async def async_main() -> None:
    client = await AsyncRconClient.create_client(host="127.0.0.1", port=27960, password="sekret")

    await client.bigtext("hello world")
    game = await client.game_info()
    if game.players:
        first_player = game.players[0]
        await client.slap(slot=first_player.slot)


if __name__ == '__main__':
    asyncio.run(async_main())
```
