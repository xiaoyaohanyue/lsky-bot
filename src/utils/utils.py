import uuid
import time
import hashlib

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


