import uuid
import time
import hashlib
import requests
import logging
import re
from src.conf.config import LSKY_VERSION
from urllib.parse import urlparse


logger = logging.getLogger(__name__)

class YyUtils:
    def __init__(self):
        pass

    def genarate_code(self):
        # 获取当前时间戳
        timestamp = str(time.time())
        # 生成一个UUID
        unique_id = str(uuid.uuid4())
        # 将时间戳和UUID拼接并生成哈希值
        combined = timestamp + unique_id
        hash_value = hashlib.sha256(combined.encode()).hexdigest()
        # 取哈希值的前8位作为随机字符串
        random_string = hash_value[:8]
        return random_string

    def get_current_time(self):
        return int(time.time())
    
    def transform_hour_to_timestamp(self, hour):
        return int(hour * 3600)
    
    def transform_timestamp_to_str(self, timestamp):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    def is_image_url(self, url):
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            response = requests.head(url, timeout=5, headers=header)
            content_type = response.headers.get('Content-Type', '')
            if content_type.startswith('image/'):
                return True
        except:
            logger.error('check_url_resource error: %s', url)
        return False
    
    def is_valid_url(self,url):
        try:
            result = urlparse(url)
            return all([result.scheme in ["http", "https"], result.netloc])
        except ValueError:
            return False
        
    def download_image(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = re.search(r'([^/]+\.(jpg|png|jpeg|gif|webp))$', url).group(1)
                type_name = self.match_image_suffix(re.findall(r'image/(\w+)', response.headers.get('Content-Type', ''))[0])
                logger.info('type_name: %s', type_name)
                if not filename:
                    filename = f'image-{int(time.time())}.{type_name}'
                target_path = f'{save_path}{filename}'
                logger.info('download_image: %s', target_path)
                with open(target_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            return {'status': True, 'path': target_path}
        except:
            logger.error('download_image error: %s', url)
            return {'status': False, 'path': ''}
    
    def match_image_suffix(self, mime_type):
        if mime_type == 'jpeg':
            return 'jpg'
        return mime_type
    
    def echo_lsky_version(self):
        if LSKY_VERSION == 'free':
            return '开源版'
        return '付费版'

