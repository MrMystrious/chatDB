from SQL import Mysql
from schema import DBSchema
from schemaFormatter import DBSchemaFormatter
from chatDB import ChatDB
from parse import Parser
from executer import Executer
from typing import List,Any
from dotenv import load_dotenv


class InitUser:
    def __init__(self,user:str,password:str,db_name:str) -> None:
        self._user = user
        self._password = password
        self._db_name = db_name
        self._key = None
        self._db = None
        self.db_details = None
        self._chat = None
        self._executer = None

    def _build_schema(self,db_name:str):
        dbSchema = DBSchema.get_dbSchema(user_key=self._key,db_name=self._db_name)
        db_details = [DBSchemaFormatter.build_DBSchemaText(db_name=self._db_name,tables=dbSchema)]
        for table in dbSchema:
            tab_name = table.get('TABLE_NAME',None)
            schema = DBSchema.get_TableSchema(user_key=self._key,tab_name=tab_name)
            sch_txt = DBSchemaFormatter.build_TableSchemaText(table_name=tab_name,table_schema=schema)
            db_details.append(sch_txt)
        self.db_details = "\n".join(db_details)

    def init(self,api_key:str,useGemini:bool=True):
        self._db = Mysql(username=self._user,password=self._password)
        self._key = self._db.connectDB(self._db_name)
        self._build_schema(self._db_name)
        self._chat = ChatDB(api_key,self.db_details)
        self._executer = Executer(self._key)
    
    def chat(self,q:str)->List[Any]:
        try:
            if not self._chat:
                raise Exception("User is not initialised.. try running init() first..")
            res = self._chat.chat(q)
            print(res)
            parsed_res = Parser.parseResponse(res)
            result = self._executer.execute(sql_cmds=parsed_res)
            return result
        except Exception as e:
            raise e 
