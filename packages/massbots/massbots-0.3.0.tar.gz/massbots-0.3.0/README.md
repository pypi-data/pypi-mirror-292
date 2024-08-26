# Python SDK

> `$ pip install massbots`

## aiogram + massbots

```python
import os
import massbots
from aiogram import Bot, Dispatcher
from aiogram import types, executor


mb = massbots.Api(os.environ["MB_TOKEN"])
bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher(bot)


@dp.message_handler()
async def on_text(msg: types.Message):
    video_id = # extract id from msg.text
    file_id = mb.dl.video_cached(video_id, "720p")
    bot.send_video(msg.chat.id, file_id)


if __name__ == "__main__":
    executor.start_polling(dp)
```
