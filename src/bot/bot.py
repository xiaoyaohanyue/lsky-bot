from telethon import TelegramClient, events, Button
from src.sql.handle import Handle
from src.bot.handle import BotHandle
from src.lsky.v1.api import LskyAPIV1
from src.lsky.v2.api import LskyAPIV2
import logging
from src.utils.utils import YyUtils
from src.conf.config import *
from telethon.tl.types import MessageMediaPhoto,MessageMediaDocument
import textwrap
logger = logging.getLogger(__name__)

class Bot():
    def __init__(self,loop):
        self.API_ID = API_ID
        self.API_HASH = API_HASH
        self.BOT_TOKEN = BOT_TOKEN
        self.client = TelegramClient(SESSION_PATH + '/bot', self.API_ID, self.API_HASH,loop=loop)
        self.SAVE_PATH = SAVE_PATH
        self.OWNER_USERNAME = OWNER_USERNAME
        self.BOT_USERNAME = BOT_USERNAME
        self.bothandle = BotHandle(self.client)
        self.LSKY_VERSION = LSKY_VERSION
        self.help_content = textwrap.dedent('''
        /start - 开始使用
        /bind - 绑定账号
        /unbind - 解绑账号
        /my - 查看图床信息
        /profile - 查看上传默认策略
        /setprofile - 设置上传默认策略
        /album - 查看相册列表
        /capacities - 查看存储列表
        /getadmins - 查看管理员列表
        /addadmin - 添加管理员
        /deladmin - 删除管理员
        /invite - 邀请用户
        /join - 使用邀请码
        /list_invited - 查看被邀请列表
''')
        
    async def enable(self):
        handle = Handle()
        if API_VERSION == 'v1':
            lsky = LskyAPIV1()
        elif API_VERSION == 'v2':
            lsky = LskyAPIV2()
        yyutils = YyUtils()
        logger.info('机器人启动中...')
        logger.info(handle.init())
        await self.client.start(bot_token=self.BOT_TOKEN)
        logger.info('机器人启动成功')
        logger.info(f'当前机器人适用于{yyutils.echo_lsky_version()}图床系统')
        owenr = await self.bothandle.get_id(self.OWNER_USERNAME)
        handle.add_owner(owenr,self.OWNER_USERNAME)
        @self.client.on(events.NewMessage())
        async def handle_message(event):
            if event.is_private:
                text = event.message.message
                if text.startswith('/'):
                    return 0
                tg_id = event.sender_id
                user_permission = handle.verify_user_permission(tg_id)
                if user_permission is None:
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                if event.message.media:
            # 检查消息是否包含图片
                    response = {}
                    if user_permission['permission'] == 'bind':
                        tgid = tg_id
                    else:
                        tgid = handle.get_invited_by_id(tg_id)
                    lsky_token = handle.get_token(tgid)
                    if isinstance(event.message.media, MessageMediaPhoto):
                        # 下载图片到指定路径
                        file_path = await self.client.download_media(event.message, self.SAVE_PATH)
                        if self.LSKY_VERSION == 'free':
                            response = lsky.upload_image(lsky_token, {'file': file_path})
                        else:
                            profile = handle.get_profile(tgid)
                            if API_VERSION == 'v1':
                                response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'permission': profile['permission']})
                            else:
                                response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'is_public': profile['permission'], 'storage_id': int(profile['storage_id'])})
                    elif isinstance(event.message.media, MessageMediaDocument):
                        mime_type = event.message.media.document.mime_type
                        if mime_type.startswith('image/'):
                            # 下载图片到指定路径
                            file_path = await self.client.download_media(event.message, self.SAVE_PATH)
                            if self.LSKY_VERSION == 'free':
                                response = lsky.upload_image(lsky_token, {'file': file_path})
                            else:
                                profile = handle.get_profile(tgid)
                                if API_VERSION == 'v1':
                                    response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'permission': profile['permission']})
                                else:
                                    response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'is_public': profile['permission'], 'storage_id': int(profile['storage_id'])})
                    elif yyutils.is_valid_url(text) and yyutils.is_image_url(text):
                        logger.info(f'检测到URL下载图片 {text}')
                        img = yyutils.download_image(text, self.SAVE_PATH)
                        if img['status']:
                            file_path = img['path']
                            if self.LSKY_VERSION == 'free':
                                response = lsky.upload_image(lsky_token, {'file': file_path})
                            else:
                                profile = handle.get_profile(tgid)
                                if API_VERSION == 'v1':
                                    response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'permission': profile['permission']})
                                else:
                                    response = lsky.upload_image(lsky_token, {'file': file_path, 'album_id': profile['album_id'], 'is_public': profile['permission'], 'storage_id': int(profile['storage_id'])})
                    else:
                        await event.reply("我只处理图片哦！")
                        return 0
                    if response['status']:
                        os.remove(file_path)
                        await self.bothandle.img_response(response, event)
                        handle.add_usage(tg_id,lsky_token,permission=user_permission['permission'])
                    else:
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        await event.reply('上传失败，请检查图片是否符合要求。')
                    
                else:
                    await event.reply("请发送图片或转发图片给我。")
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start(event):
            if event.is_private:
                tg_id = event.sender_id
                if handle.check_block_list(tg_id):
                    await event.respond(f'你已被拉黑，请联系 @{self.OWNER_USERNAME} 解除')
                    return 0
                args = event.message.message.split(' ')
                if len(args) == 2:
                    if args[1].startswith('invite_'):
                        invite_code = args[1].split('_')[1]
                        verify = handle.verify_invite_code(invite_code)
                        if not verify:
                            await event.respond('邀请码已失效')
                            return 0
                        elif handle.get_token(tg_id) is not None:
                            await event.respond('你已绑定账号，无法使用该功能')
                            return 0
                        else:
                            handle.add_invited_user(tg_id,invite_code)
                            await event.respond('邀请码使用成功！')
                            return 0
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                await event.respond('欢迎使用！')
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help(event):
            if event.is_private:
                await event.respond(self.help_content)

        @self.client.on(events.NewMessage(pattern='/album'))
        async def album(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                token = handle.get_token(tg_id)
                res = lsky.albums(token)
                if res['status']:
                    msg = '相册列表:\n'
                    for album in res['albums']:
                        msg += f'{album["id"]} - {album["name"]}\n'
                    await event.respond(msg)
                else:
                    await event.respond('获取相册列表失败，请检查token是否正确。')
        
        @self.client.on(events.NewMessage(pattern='/capacities'))
        async def capacities(event):
            if event.is_private:
                tg_id = event.sender_id
                if API_VERSION == 'v1':
                    await event.respond('该功能仅适用于v2版本')
                    return 0
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                token = handle.get_token(tg_id)
                res = lsky.capacities(token)
                if res['status']:
                    msg = '存储列表:\n'
                    for capacities in res['capacities']:
                        msg += f'{capacities["id"]} - {capacities["name"]}\n'
                    await event.respond(msg)
                else:
                    await event.respond('获取存储列表失败，请检查token是否正确。')
        
        @self.client.on(events.NewMessage(pattern='/my'))
        async def my(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                token = handle.get_token(tg_id)
                res = lsky.me(token)
                if res['status']:
                    msg = textwrap.dedent(f'''
                    用户名: {res['username']}
                    昵称: {res['name']}
                    邮箱: {res['email']}
                    容量: {round(res['capacity']/1024/1024)}GB
                    已用: {round(res['used']/1024/1024,2)}GB
                    图片数量: {res['image_num']}
                    ''')
                    await event.respond(msg)
                else:
                    await event.respond('获取信息失败，请检查token是否正确。')

        @self.client.on(events.NewMessage(pattern='/profile'))
        async def profile(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                if self.LSKY_VERSION == 'free':
                    await event.respond('开源版无需设置上传策略')
                    return 0
                profile = handle.get_profile(tg_id)
                if profile:
                    msg = textwrap.dedent(f'''
                    上传策略: 
                    图片权限: {'公开' if profile['permission'] == 1 else '私有'}
                    上传相册ID: {profile['album_id']}
                    存储ID: {profile['storage_id']}
                    ''')
                    await event.respond(msg)
                else:
                    await event.respond('获取信息失败，请检查token是否正确。')
        
        @self.client.on(events.NewMessage(pattern='/setprofile'))
        async def set_profile(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                message = event.message.message
                arg_count = message.split(' ')
                if API_VERSION == 'v1':
                    if len(arg_count) != 3:
                        await event.respond('请按照 /setprofile 权限 相册ID 格式发送')
                        return 0
                    if self.LSKY_VERSION == 'free':
                        await event.respond('开源版无需设置上传策略')
                        return 0
                    permission = arg_count[1]
                    album_id = arg_count[2]
                    if permission not in ['1','0']:
                        await event.respond('权限只能是 1 或 0')
                        return 0
                    if not album_id.isdigit():
                        await event.respond('相册ID只能是数字')
                        return 0
                    token = handle.get_token(tg_id)
                    handle.update_lsky_profile(token,album_id,permission)
                else:
                    if len(arg_count) != 4:
                        await event.respond('请按照 /setprofile 权限 相册ID 存储ID 格式发送')
                        return 0
                    permission = arg_count[1]
                    album_id = arg_count[2]
                    storage_id = arg_count[3]
                    if permission not in ['1','0']:
                        await event.respond('权限只能是 1 或 0')
                        return 0
                    if not album_id.isdigit():
                        await event.respond('相册ID只能是数字')
                        return 0
                    if not storage_id.isdigit():
                        await event.respond('存储ID只能是数字')
                        return 0
                    token = handle.get_token(tg_id)
                    handle.update_lsky_profile(token,album_id,permission,storage_id)
                await event.respond('设置成功！')
        

        @self.client.on(events.NewMessage(pattern='/bind'))
        async def bind(event):
            if event.is_private:
                tg_id = event.sender_id
                if handle.check_block_list(tg_id):
                    await event.respond(f'你已被拉黑，请联系 @{self.OWNER_USERNAME} 解除')
                    return 0
                message = event.message.message
                arg_count = message.split(' ')
                if self.LSKY_VERSION == 'free':
                    if len(arg_count) != 3:
                        await event.respond('请按照 /bind 图床账号 图床密码 格式发送')
                        return 0
                    res = lsky.get_token({'email':arg_count[1],'password':arg_count[2]})
                    if res['status']:
                        token = res['token']
                    else:
                        await event.respond('绑定失败，请检查账号密码是否正确')
                        return 0
                else:
                    if len(arg_count) != 2:
                        await event.respond('请按照 /bind token 格式发送')
                        return 0
                    token = arg_count[1]
                if lsky.me(token)['status']:
                    handle.update_user(tg_id,token)
                    await event.respond('绑定成功！')
                else:
                    handle.update_bind_error_times(tg_id)
                    if handle.get_bind_error_times(tg_id) >= 3:
                        handle.update_block_list(tg_id)
                        await event.respond(f'绑定失败次数过多，已被拉黑，请联系 @{self.OWNER_USERNAME} 解除')
                        return 0
                    await event.respond('绑定失败，请检查token是否正确，三次失败后会被拉黑。')
        
        @self.client.on(events.NewMessage(pattern='/unbind'))
        async def unbind(event):
            if event.is_private:
                tg_id = event.sender_id
                handle.remove_user(tg_id)
                await event.respond('解绑成功！')

        @self.client.on(events.NewMessage(pattern='/block'))
        async def block(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_admin(tg_id):
                    await event.respond('你没有权限')
                    return 0
                message = event.message.message
                input = message.split('-b')
                if len(input) != 2:
                    await event.respond('请按照 /block -b 用户名 格式发送')
                    return 0
                user = input[1].strip()
                user_id = await self.bothandle.get_id(user)
                handle.update_block_list(user_id)
                await event.respond('拉黑成功！')

        @self.client.on(events.NewMessage(pattern='/unblock'))
        async def unblock(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_admin(tg_id):
                    await event.respond('你没有权限')
                    return 0
                message = event.message.message
                input = message.split('-b')
                if len(input) != 2:
                    await event.respond('请按照 /unblock -b 用户名 格式发送')
                    return 0
                user = input[1].strip()
                user_id = await self.bothandle.get_id(user)
                handle.remove_block_list(user_id)
                await event.respond('解除拉黑成功！')

        @self.client.on(events.NewMessage(pattern='/getadmins'))
        async def get_admins(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_admin(tg_id):
                    await event.respond('你没有权限')
                    return 0
                admins = handle.get_admin()
                msg = '管理员列表:\n'
                for admin in admins:
                    msg += f'{admin["tg_id"]} - {admin["username"]}\n'
                await event.respond(msg)
        
        @self.client.on(events.NewMessage(pattern='/addadmin'))
        async def add_admin(event):
            if event.is_private:
                tg_id = event.sender_id
                print(tg_id)
                if not handle.check_owner(str(tg_id)):
                    await event.respond('你没有权限')
                    return 0
                message = event.message.message
                arg_count = message.split(' ')
                if len(arg_count) != 2:
                    await event.respond('请按照 /addadmin 用户名 格式发送')
                    return 0
                user = arg_count[1]
                user_id = await self.bothandle.get_id(user)
                handle.add_admin(user_id,user)
                await event.respond('添加成功！')

        @self.client.on(events.NewMessage(pattern='/deladmin'))
        async def del_admin(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_owner(str(tg_id)):
                    await event.respond('你没有权限')
                    return 0
                message = event.message.message
                arg_count = message.split(' ')
                if len(arg_count) != 2:
                    await event.respond('请按照 /deladmin 用户名 格式发送')
                    return 0
                user = arg_count[1]
                await event.respond(handle.remove_admin(user))

        @self.client.on(events.NewMessage(pattern='/invite'))
        async def invite(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                message = event.message.message
                args = message.split(' ')
                if len(args) != 4:
                    await event.respond('请按照 /invite 被邀请人可用次数 邀请码有效次数(-1为不限次) 邀请码有效时长(n小时，-1为不限时) 格式发送')
                    return 0
                times = args[1]
                count = args[2]
                expire_time = args[3]
                if not times.isdigit() or not count.isdigit() or not expire_time.isdigit():
                    await event.respond('可用次数、邀请码有效次数、邀请码有效时长只能是数字')
                    return 0
                if int(times) < 1:
                    await event.respond('被邀请人可用次数不能小于1')
                    return 0
                if int(count) < -1 or int(expire_time) < -1:
                    await event.respond('邀请码有效次数、邀请码有效时长不能小于-1')
                    return 0
                invite_code = handle.genarate_invite_code(tg_id,int(times),int(count),int(expire_time))
                invite_link = f'https://t.me/{self.BOT_USERNAME}?start=invite_{invite_code}'
                msg = textwrap.dedent(f'''
                邀请码: {invite_code}
                邀请链接: {invite_link}
                邀请码使用方式：/join 邀请码
                邀请链接使用方式：点击链接即可
                ''')
                buttons = [
                    [Button.url("点击获得临时权限", url=invite_link)],
                ]
                await event.respond(msg, buttons=buttons)
        
        @self.client.on(events.NewMessage(pattern='/join'))
        async def join(event):
            if event.is_private:
                tg_id = event.sender_id
                if handle.check_block_list(tg_id):
                    await event.respond(f'你已被拉黑，请联系 @{self.OWNER_USERNAME} 解除')
                    return 0
                if handle.check_invite_user(tg_id):
                    await event.respond('你已被邀请，等待次数使用完后再次接受邀请')
                    return 0
                if handle.get_token(tg_id) is not None:
                    await event.respond('你已绑定账号，无法使用该功能')
                    return 0
                message = event.message.message
                args = message.split(' ')
                if len(args) != 2:
                    await event.respond('请按照 /join 邀请码 格式发送')
                    return 0
                invite_code = args[1]
                verify = handle.verify_invite_code(invite_code)
                if not verify:
                    await event.respond('邀请码已失效')
                    return 0
                else:
                    handle.add_invited_user(tg_id,invite_code)
                    await event.respond('邀请码使用成功！')
                    return 0
        
        @self.client.on(events.NewMessage(pattern='/list_invited'))
        async def list_invited(event):
            if event.is_private:
                tg_id = event.sender_id
                if not handle.check_bind(tg_id):
                    await event.respond('请先绑定账号，发送 /bind token 进行绑定。')
                    return 0
                invited_users = handle.get_list_invited_user(tg_id)
                msg = '被邀请列表: ID - 可用次数 - 邀请时间 - 状态\n'
                for user in invited_users:
                    msg += f'{user["tg_id"]} - {user["times"]} - {user["invite_time"]} - {user["status"]}\n'
                    await event.respond(msg)
        
        
                
        

                


