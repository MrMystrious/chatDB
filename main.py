from SQL import Mysql
from schema import DBSchema
from schemaFormatter import DBSchemaFormatter
from chatDB import ChatDB
from pool import PoolManager
from parse import Parser
import os
from dotenv import load_dotenv
from executer import Executer
from init_user import InitUser

load_dotenv()

db_name = "sakila"



user = InitUser(os.getenv("MYSQL_USERNAME"),os.getenv("MYSQL_PASSWORD"),db_name)
user.init(os.getenv("GEMINI_API_KEY"))

quries = ["Find the top 3 most rented films per category.",
        ]

for q in quries:
    print(f"\nquery : {q}")
    res = user.chat(q)
    print(res,'\n\n')