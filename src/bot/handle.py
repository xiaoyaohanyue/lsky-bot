import logging
import textwrap
from src.conf.config import LSKY_VERSION,API_VERSION

logger = logging.getLogger(__name__)


class BotHandle():
    def __init__(self, client):
        self.client = client

    async def get_id(self, username):
        id = await self.client.get_peer_id(username)
        return id
    
    async def img_response(self,response: dict, event):
        if API_VERSION == 'v1':
            if LSKY_VERSION == 'free':
                msg = textwrap.dedent(f'''
                    上传成功！
                    图片链接: `{response['links']['url']}`
                    HTML链接: `{response['links']['html']}`
                    BBCode链接: `{response['links']['bbcode']}`
                    Markdown链接: `{response['links']['markdown']}`
                    Markdown带链接: `{response['links']['markdown_with_link']}`
                    缩略图: `{response['links']['thumbnail_url']}`
                    ''')
                await event.reply(msg)
            elif LSKY_VERSION == 'paid':
                msg = textwrap.dedent(f'''
                    上传成功！
                    图片链接: `{response['links']['url']}`
                    HTML链接: `{response['links']['html']}`
                    BBCode链接: `{response['links']['bbcode']}`
                    Markdown链接: `{response['links']['markdown']}`
                    Markdown带链接: `{response['links']['markdown_with_link']}`
                    缩略图: `{response['links']['thumbnail_url']}`
                    删除链接: `{response['links']['delete_url']}`
                    ''')
        else:
            print(response)
            msg = textwrap.dedent(f'''
                上传成功！
                图片链接: `{response['links']}`
                ''')
        await event.reply(msg)
