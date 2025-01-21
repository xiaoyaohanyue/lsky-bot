import sqlite3

class qlite3:   
    def __init__(self,sqlite_file) -> None:
        self.sqlite_file = sqlite_file


    def exec(self,cmd,is_update=False):
        __conn = sqlite3.connect(self.sqlite_file)
        __sql3_cursor = __conn.cursor()
        __sql3_cursor.execute(cmd)
        if is_update:
            __conn.commit()
        __conn.close()

    def query(self,cmd,is_all=False):
        __conn = sqlite3.connect(self.sqlite_file)
        __sql3_cursor = __conn.cursor()
        __sql3_cursor.execute(cmd)
        if is_all:
            myresult = __sql3_cursor.fetchall()
        else:
            myresult = __sql3_cursor.fetchone()
        __conn.close()
        return myresult
    
    def check_table(self,table_name):
        cmd = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        result = self.query(cmd,False)
        if result:
            return True
        else:
            return False
  
