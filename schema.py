from pool import PoolManager
from SQL import Mysql
from typing import Union,List,Dict

class DBSchema:
    @classmethod
    def get_dbSchema(cls,user_key:str,db_name:str)->Union[List[dict],int,None]:
        try:
            query = """SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s;"""
            result = Mysql.execute(key=user_key,sql=query,params=(db_name,))
            return result
        except Exception as e:
            print("Error has occured in getting the db_schema...")
            raise e
    
    @classmethod
    def get_TableSchema(cls,user_key:str,tab_name:str)->Union[List[dict],int,None]:
        try:
            db_name = PoolManager.get_user_db(user_key=user_key)
            query = """SELECT column_name, data_type, is_nullable, column_key
FROM information_schema.columns
WHERE table_schema = %s
AND table_name = %s;
"""
            result = Mysql.execute(key=user_key,sql=query,params=(db_name,tab_name))
            return result
        except Exception as e:
            print(f"Error has occured in getting the db_schema...{e}")

    