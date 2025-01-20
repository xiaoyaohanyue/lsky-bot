from src.sql.sql import qlite3
from conf.config import SQL_PATH
from src.utils.utils import YyUtils
import logging

logger = logging.getLogger(__name__)

class Handle:
    def __init__(self) -> None:
        self.sqlite_file = SQL_PATH + '/yaoyue.db'
        self.__sql = qlite3(self.sqlite_file)
        self.table_list = ['user', 'lsky_profile', 'usage', 'block_list', 'bind_error_times', 'admin', 'invited_user', 'invite_code', 'invite_log']
        self.yyutils = YyUtils()

    def create_table(self,table_name):
        if table_name == 'user':
            cmd = 'CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, lsky_token TEXT);'
        if table_name == 'lsky_profile':
            cmd = 'CREATE TABLE lsky_profile (id INTEGER PRIMARY KEY AUTOINCREMENT, lsky_token TEXT, permission INTEGER, album_id INTEGER);'
        if table_name == 'usage':
            cmd = 'CREATE TABLE usage (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, times TEXT, lsky_token TEXT);'
        if table_name == "block_list":
            cmd = "CREATE TABLE block_list (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT);"
        if table_name == "bind_error_times":
            cmd = "CREATE TABLE bind_error_times (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, times INTEGER);"
        if table_name == "admin":
            cmd = "CREATE TABLE admin (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, username TEXT, type TEXT);"
        if table_name == "invited_user":
            cmd = "CREATE TABLE invited_user (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, times INTEGER, invited_by TEXT, invite_code TEXT, lsky_token TEXT);"
        if table_name == "invite_code":
            cmd = "CREATE TABLE invite_code (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, times INTEGER, tg_id TEXT, expired_time TEXT, count INTEGER);"
        if table_name == "invite_log":
            cmd = "CREATE TABLE invite_log (id INTEGER PRIMARY KEY AUTOINCREMENT, tg_id TEXT, code TEXT, invited_by TEXT, invite_time TEXT, status INTEGER);"
        self.__sql.exec(cmd,True)

    def check_table(self,table_name):
        res = self.__sql.check_table(table_name)
        return res
    
    def check_exist(self, sql):
        res = self.__sql.query(sql)
        if res:
            return True
        else:
            return False
    
    def verify_user_permission(self, tg_id):
        if self.check_bind(tg_id):
            return {"status": True, "permission": 'bind'}
        elif self.check_invite_user(tg_id):
            return {"status": True, "permission": 'invite'}
        else:
            return None
        
    def get_token(self, tg_id):
        cmd = f"SELECT lsky_token FROM user WHERE tg_id = '{tg_id}'"
        res = self.__sql.query(cmd)
        if res:
            return res[0]
        else:
            return None
    
    def get_token_invited(self, tg_id):
        cmd = f"SELECT lsky_token FROM invited_user WHERE tg_id = '{tg_id}'"
        res = self.__sql.query(cmd)
        if res:
            return res[0]
        else:
            return None
    
    def get_invited_by_id(self, tg_id):
        cmd = f"SELECT invited_by FROM invited_user WHERE tg_id = '{tg_id}'"
        res = self.__sql.query(cmd)
        if res:
            return res[0]
        else:
            return None
    
    
    def update_invite_log(self, tg_id, code, invited_by,status):
        if status == 1:
            cmd = f"INSERT INTO invite_log (tg_id, code, invited_by, invite_time) VALUES ('{tg_id}', '{code}', '{invited_by}', '{self.yyutils.get_current_time()}')"
        else:
            cmd = f"UPDATE invite_log SET status = 0 WHERE tg_id = '{tg_id}' AND code = '{code}' AND invited_by = '{invited_by}'"
        self.__sql.exec(cmd,True)

    def genarate_invite_code(self, tg_id, times, count, expired_time):
        code = self.yyutils.genarate_code()
        while self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            code = self.yyutils.genarate_code()
        if expired_time == -1:
            expired_time = -1
        else:
            expired_time = self.yyutils.transform_hour_to_timestamp(expired_time) + self.yyutils.get_current_time()
        self.update_invite_code(tg_id, code, expired_time, times, count)
        return code
    
    def update_invite_code(self, tg_id, code, expired_time, times, count):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            return False
        cmd = f"INSERT INTO invite_code (code, times, tg_id, expired_time,count) VALUES ('{code}', {times}, '{tg_id}', '{expired_time}', '{count}')"
        self.__sql.exec(cmd,True)
        return True
    
    def get_expire_invite_code(self,code):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            cmd = f"SELECT expired_time FROM invite_code WHERE code = '{code}'"
            res = self.__sql.query(cmd)
            return int(res[0])
        else:
            return None
        
    def verify_invite_code(self, code):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            expired_time = self.get_expire_invite_code(code)
            if expired_time == -1:
                remian_times = self.get_remain_invite_code(code)
                if remian_times != 0:
                    return True
                else:
                    return False
            elif expired_time > self.yyutils.get_current_time():
                remian_times = self.get_remain_invite_code(code)
                if remian_times != 0:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    
    def get_invite_code_info(self, code):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            cmd = f"SELECT tg_id, times, expired_time, count FROM invite_code WHERE code = '{code}'"
            res = self.__sql.query(cmd)
            return {"tg_id": res[0], "times": res[1], "expired_time": res[2], "count": res[3]}
        else:
            return None
    def get_remain_invite_code(self, code):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}'"):
            cmd = f"SELECT count FROM invite_code WHERE code = '{code}'"
            res = self.__sql.query(cmd)
            if res[0] != -1:
                return int(res[0])
            else:
                return None
        else:
            return None
        
    def update_remain_invite_code(self, code):
        if self.check_exist(f"SELECT * FROM invite_code WHERE code = '{code}' and count != 0"):
            remian_count = self.get_remain_invite_code(code)
            if remian_count == None:
                return False
            count = int(remian_count) - 1
            if count >= 0:                                                                                    
                cmd = f"UPDATE invite_code SET count = {count} WHERE code = '{code}'"
            else:
                cmd = f"DELETE FROM invite_code WHERE code = '{code}'"
            self.__sql.exec(cmd,True)
    
    def check_invite_user(self, tg_id):
        if self.check_exist(f"SELECT * FROM invited_user WHERE tg_id = '{tg_id}' and times != 0"):
            return True
        else:
            return False
        
    def add_invited_user(self, tg_id, invite_code):
        if self.check_invite_user(tg_id):
            return False
        code_info = self.get_invite_code_info(invite_code)
        if code_info == None:
            return False
        invited_by = code_info["tg_id"]
        times = code_info["times"]
        lsky_token = self.get_token(invited_by)
        cmd = f"INSERT INTO invited_user (tg_id, times, invited_by, invite_code, lsky_token) VALUES ('{tg_id}', {times}, '{invited_by}', '{invite_code}', '{lsky_token}')"
        self.__sql.exec(cmd,True)
        self.update_remain_invite_code(invite_code)
        self.add_usage(tg_id, lsky_token, permission='invite')
        self.update_invite_log(tg_id, invite_code, invited_by, 1)
        return True
    
    def get_remin_times(self, tg_id):
        if self.check_invite_user(tg_id):
            cmd = f"SELECT times FROM invited_user WHERE tg_id = '{tg_id}'"
            res = self.__sql.query(cmd)
            return int(res[0])
        else:
            return None
        
    def get_list_invited_user(self, tg_id):
        cmd = f"SELECT tg_id,code,invite_time,status FROM invite_log WHERE invited_by = '{tg_id}'"
        user = []
        res = self.__sql.query(cmd,True)
        if not res:
            return None
        for i in res:
            user.append({"tg_id": i[0], "code": i[1], "invite_time": self.yyutils.transform_timestamp_to_str(int(i[2])), "status": "有效" if i[3] == 1 else "失效"})
        return user
    
    def get_invited_user(self, tg_id):
        if self.check_invite_user(tg_id):
            cmd = f"SELECT tg_id,times,invited_by,invite_code,lsky_token FROM invited_user WHERE tg_id = '{tg_id}'"
            res = self.__sql.query(cmd)
            return {"tg_id": res[0], "times": res[1], "invited_by": res[2], "invite_code": res[3], "lsky_token": res[4]}
        else:
            return None
    
    def update_invited_user(self, tg_id):
        if self.check_invite_user(tg_id):
            remian_times = self.get_remin_times(tg_id)
            if remian_times == 1 or remian_times == 0:
                user_info = self.get_invited_user(tg_id)
                invited_by = user_info["invited_by"]
                invite_code = user_info["invite_code"]
                self.update_invite_log(tg_id, invite_code, invited_by, 0)
                self.remove_invited_user(tg_id)
                return True
            elif remian_times == None:
                return False
            elif remian_times < 0:
                return True
            cmd = f"UPDATE invited_user SET times = {remian_times}-1 WHERE tg_id = '{tg_id}'"
            self.__sql.exec(cmd,True)
            return True
    
    def remove_invited_user(self, tg_id):
        if self.check_invite_user(tg_id):
            cmd = f"DELETE FROM invited_user WHERE tg_id = '{tg_id}'"
            self.__sql.exec(cmd,True)
            return True

    
    def update_bind_error_times(self, tg_id):
        if self.check_exist(f"SELECT * FROM bind_error_times WHERE tg_id = '{tg_id}'"):
            cmd = f"UPDATE bind_error_times SET times = times + 1 WHERE tg_id = '{tg_id}'"
        else:
            cmd = f"INSERT INTO bind_error_times (tg_id, times) VALUES ('{tg_id}', '1')"
        self.__sql.exec(cmd,True)

    def get_bind_error_times(self, tg_id):
        if self.check_exist(f"SELECT * FROM bind_error_times WHERE tg_id = '{tg_id}'"):
            cmd = f"SELECT times FROM bind_error_times WHERE tg_id = '{tg_id}'"
            res = self.__sql.query(cmd)
            return int(res[0])
        else:
            return 0
    
    def remove_bind_error_times(self, tg_id):
        if self.check_exist(f"SELECT * FROM bind_error_times WHERE tg_id = '{tg_id}'"):
            cmd = f"DELETE FROM bind_error_times WHERE tg_id = '{tg_id}'"
            self.__sql.exec(cmd,True)
        
    def update_block_list(self, tg_id):
        if self.check_exist(f"SELECT * FROM block_list WHERE tg_id = '{tg_id}'"):
            return True
        cmd = f"INSERT INTO block_list (tg_id) VALUES ('{tg_id}')"
        self.__sql.exec(cmd,True)
    
    def remove_block_list(self, tg_id):
        cmd = f"DELETE FROM block_list WHERE tg_id = '{tg_id}'"
        self.__sql.exec(cmd,True)
        self.remove_bind_error_times(tg_id)

    def check_block_list(self, tg_id):
        if self.check_exist(f"SELECT * FROM block_list WHERE tg_id = '{tg_id}'"):
            return True
        else:
            return False

    def get_times_from_usage(self, tg_id, token):
        cmd = f"SELECT times FROM usage WHERE tg_id = '{tg_id}' and lsky_token = '{token}'"
        res = self.__sql.query(cmd)
        if not res: 
            return None
        return int(res[0])

    def update_usage(self, tg_id, token):
        times = self.get_times_from_usage(tg_id, token)
        if times == None:
            return 0
        times = int(times) + 1
        cmd = f"UPDATE usage SET times = {times} WHERE tg_id = '{tg_id}' and lsky_token = '{token}'"
        self.__sql.exec(cmd,True)
    
    def add_usage(self, tg_id, token, permission):
        if self.check_exist(f"SELECT * FROM usage WHERE tg_id = '{tg_id}' and lsky_token = '{token}'"):
            self.update_usage(tg_id,token)
            if permission == 'invite':
                self.update_invited_user(tg_id)
            return 0
        cmd = f"INSERT INTO usage (tg_id, times, lsky_token) VALUES ('{tg_id}', '0', '{token}')"
        self.__sql.exec(cmd,True)

    def remove_user(self, tg_id):
        cmd = f"DELETE FROM user WHERE tg_id = '{tg_id}'"
        self.__sql.exec(cmd,True)

    def check_bind(self, tg_id):
        if self.check_exist(f"SELECT * FROM user WHERE tg_id = '{tg_id}'"):
            return True
        else:
            return False
    
    def get_profile(self, tg_id):
        token = self.get_token(tg_id)
        cmd = f"SELECT permission,album_id FROM lsky_profile WHERE lsky_token = '{token}'"
        res = self.__sql.query(cmd)
        if not res:
            return False
        return {"permission": res[0], "album_id": res[1]}
    
    def update_user(self, tg_id, lsky_token):
        if self.check_exist(f"SELECT * FROM user WHERE tg_id = '{tg_id}'"):
            cmd = f"UPDATE user SET lsky_token = '{lsky_token}' WHERE tg_id = '{tg_id}'"
        else:
            cmd = f"INSERT INTO user (tg_id, lsky_token) VALUES ('{tg_id}', '{lsky_token}')"
        self.__sql.exec(cmd,True)
        self.add_usage(tg_id, lsky_token, 'bind')
        self.update_lsky_profile(lsky_token, 0, 0)
    
    def update_lsky_profile(self, lsky_token, album_id, permission=None):
        if permission == None:
            permission = 0
        if self.check_exist(f"SELECT * FROM lsky_profile WHERE lsky_token = '{lsky_token}'"):
            cmd = f"UPDATE lsky_profile SET permission = '{permission}', album_id = '{album_id}' WHERE lsky_token = '{lsky_token}'"
        else:
            cmd = f"INSERT INTO lsky_profile (lsky_token, permission, album_id) VALUES ('{lsky_token}', '{permission}', '{album_id}')"
        self.__sql.exec(cmd,True)

    def check_admin(self, tg_id):
        if self.check_exist(f"SELECT * FROM admin WHERE tg_id = '{tg_id}'"):
            return True
        else:
            return False
        
    def check_owner(self, input):
        if input.isdigit():
            tg_id = input
            if self.check_exist(f"SELECT * FROM admin WHERE tg_id = '{tg_id}' AND type = 'owner'"):
                return True
            else:
                return False
        else:
            username = input
            if self.check_exist(f"SELECT * FROM admin WHERE username = '{username}' AND type = 'owner'"):
                return True
            else:
                return False
            
    def get_admin(self):
        cmd = f"SELECT username,tg_id,type FROM admin"
        admins = []
        res = self.__sql.query(cmd,True)
        for i in res:
            admins.append({"username": i[0], "tg_id": i[1], "type": "管理员" if i[2] == "admin" else "拥有者"})
        return admins
    
    def add_admin(self, tg_id, username):
        cmd = f"INSERT INTO admin (tg_id, username, type) VALUES ('{tg_id}', '{username}', 'admin')"
        self.__sql.exec(cmd,True)
        return '添加成功！'
    
    def remove_admin(self, username):
        if self.check_owner(username):
            return '拥有者不能删除！'
        if not self.check_exist(f"SELECT * FROM admin WHERE username = '{username}'"):
            return '用户不存在！'
        cmd = f"DELETE FROM admin WHERE username = '{username}'"
        self.__sql.exec(cmd,True)
        return '删除成功！'
    
    def add_owner(self, tg_id, username):
        if self.check_exist(f"SELECT * FROM admin WHERE username = '{username}'"):
            logger.info(f"用户{username}已经存在！")
            return 0
        cmd = f"INSERT INTO admin (tg_id, username, type) VALUES ('{tg_id}', '{username}', 'owner')"
        self.__sql.exec(cmd,True)
        logger.info(f"添加用户{username}为拥有者！")
        return 0

    def init(self):
        for table in self.table_list:
            if not self.check_table(table):
                self.create_table(table)
        
        
    