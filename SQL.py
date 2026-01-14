import re
import os
import hashlib
from dotenv import load_dotenv
from mysql.connector import pooling
from pool import PoolManager
from typing import Optional,Union,List,Any
load_dotenv()

MAX_ROWS = 1000

import re

class SQLDialectError(RuntimeError):
    pass


class MySQLDialectGuard:
    """
    Enforces MySQL-specific SQL syntax.
    """

    # PostgreSQL-only or non-MySQL constructs
    FORBIDDEN_PATTERNS = [
        r"\bILIKE\b",
        r"\bRETURNING\b",
        r"\bFILTER\s*\(",
        r"::\w+",
        r"\bSERIAL\b",
        r"\bON\s+CONFLICT\b",
        r"\bLIMIT\s+ALL\b",
    ]

    # TEMP TABLE is illegal in MySQL (must be TEMPORARY)
    TEMP_TABLE_PATTERN = re.compile(
        r"\bCREATE\s+TEMP\s+TABLE\b",
        re.IGNORECASE
    )

    @classmethod
    def enforce_mysql(cls, sql: str) -> str:
        sql_clean = sql.strip()

        # Hard block forbidden constructs
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, sql_clean, re.IGNORECASE):
                raise SQLDialectError(
                    f"Non-MySQL SQL detected: {pattern}"
                )

        # Normalize TEMP TABLE → TEMPORARY TABLE
        if cls.TEMP_TABLE_PATTERN.search(sql_clean):
            sql_clean = cls.TEMP_TABLE_PATTERN.sub(
                "CREATE TEMPORARY TABLE",
                sql_clean
            )

        return sql_clean

class SQLSafetyGuard:
    READ_ONLY_PATTERN = re.compile(
        r"^\s*(WITH\s+[\s\S]+?\s+SELECT|SELECT)\b",
        re.IGNORECASE
    )

    FORBIDDEN_PATTERN = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE)\b",
        re.IGNORECASE
    )

    @classmethod
    def enforce_read_only(cls, sql: str) -> None:
        sql_clean = sql.strip()

        if not cls.READ_ONLY_PATTERN.match(sql_clean):
            raise RuntimeError(
                "Only SELECT or WITH SELECT queries are allowed"
            )

        if cls.FORBIDDEN_PATTERN.search(sql_clean):
            raise RuntimeError(
                "Query contains forbidden keywords (DDL/DML not allowed)"
            )


class Mysql:
    def __init__(self,username,password,port=os.getenv("MYSQL_PORT",3306),host=os.getenv("MYSQL_HOST","localhost")) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.pool:Optional[pooling.MySQLConnectionPool] = None
        
    
    def make_identity(self,db_name:str):
        raw = f"{self.username}|{self.password}|{db_name}|{self.host}|{self.port}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def connectDB(self,db_name:str)->str:
        try:
            key = self.make_identity(db_name=db_name)
            self.pool = PoolManager.create_pool(user_key=key,user=self.username,password=self.password,host=self.host,port=self.port,db_name=db_name)
            return key
        except Exception as e:
            print(f"Error in connecting to DB {e}")
            raise

    def execute_query(self,sql:str,params:Optional[Union[List[Any],tuple]]=None)->Union[List[dict],int,None]: 
        if not self.pool:
            raise RuntimeError("Connecting pool is not initialised")
        sql = MySQLDialectGuard.enforce_mysql(sql)
        SQLSafetyGuard.enforce_read_only(sql)
        conn = self.pool.get_connection()  
        try:  
            with conn.cursor(dictionary=True,buffered=False) as cursor:
                cursor.execute(sql,params)
                if cursor.with_rows:
                    rows = cursor.fetchmany(MAX_ROWS+1)
                    if len(rows) > MAX_ROWS:
                        raise RecursionError("Result is too large.. try asking limit or aggregation result in your query")
                    return rows
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"Error in executing the query {e}")
            raise
        finally:
            conn.close()

    @classmethod
    def execute(cls,key:str,sql:str,params:Optional[Union[List[Any],tuple]]=None)->Union[List[dict],int,None]: 
        sql = MySQLDialectGuard.enforce_mysql(sql)
        SQLSafetyGuard.enforce_read_only(sql)
        conn = PoolManager.get_pool(user_key=key).get_connection()  
        try:  
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql,params)
                if cursor.with_rows:
                    rows = cursor.fetchmany(MAX_ROWS+1)
                    if len(rows) > MAX_ROWS:
                        raise RecursionError("Result is too large.. try asking limit or aggregation result in your query")
                    return rows
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Error in executing the query {e}")
            raise
        finally:
            conn.close()
