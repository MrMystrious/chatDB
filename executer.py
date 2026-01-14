from typing import List,Dict,Any
from SQL import Mysql

class Executer:
    def __init__(self,key:str) -> None:
        self.key = key
    def execute(self,sql_cmds:List[Dict[str,str]])->List[Any]:
        results = []
        for sql in sql_cmds:
            stmt = sql.get('sql',None)
            if not stmt:
                continue
            res = Mysql.execute(self.key,stmt)
            results.append(res)
        
        return results