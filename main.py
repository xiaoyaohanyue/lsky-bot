from src.bot.bot import Bot
import asyncio
from src.init import yyinit

def main():
    loop = asyncio.get_event_loop()
    BOT = Bot(loop)
    loop.create_task(BOT.enable())
    loop.run_forever()
init = yyinit()
init.init()
main()
