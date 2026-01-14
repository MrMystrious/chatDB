import os
from dotenv import load_dotenv
from mysql.connector import pooling
load_dotenv()

class PoolManager:
    pool = {}
    db = {}
    @classmethod
    def create_pool(cls,user_key:str,user:str,password:str,host:str,port,db_name = "chatdb_test"):
        key = user_key
        if key not in cls.db:
            cls.db[key] = db_name
        if key not in cls.pool:
            cls.pool[key] = pooling.MySQLConnectionPool(
                pool_name=f"pool_{user}",
                pool_size=5,
                host=host,
                user=user,
                port=port,
                password=password,
                database=db_name
            )
        return cls.pool[key]
    
    @classmethod
    def get_pool(cls,user_key:str)->pooling.MySQLConnectionPool:
        if user_key not in cls.pool:
            raise KeyError("The key of this particular user is not created... Try calling create_pool first...")
        else:
            return cls.pool[user_key]
    
    @classmethod
    def get_user_db(cls,user_key:str)->str:
        try:
            if user_key not in cls.db:
                raise Exception("The passed key is not registered in db, run create_pool() to generate key")
            else:
                return cls.db[user_key]
        except Exception as e:
            print(f"Exception Occured...{e}")