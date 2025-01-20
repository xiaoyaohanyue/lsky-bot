from src.bot.bot import Bot
import getopt,sys,asyncio,logging,os
from src.init import yyinit
from src.lsky.api import LskyAPI

def main():
    loop = asyncio.get_event_loop()
    BOT = Bot(loop)
    loop.create_task(BOT.enable())
    loop.run_forever()
init = yyinit()
init.init()
main()

# api = LskyAPI()
# res = api.me("3|yJCrAL6D5YulzzKkeGSn2aQECEaPLBtp9iEt4UCX1")
# print(res)
# token = '3|yJCrAL6D5YulzzKkeGSn2aQECEaPLBtp9iEt4UCX'
# lsky = LskyAPI()
# # res = lsky.upload_image(token, {'file': 'data/hkhk.png', 'album_id': 8})
# res = lsky.me(token)['status']
# print(res)