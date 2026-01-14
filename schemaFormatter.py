from typing import List, Dict


class DBSchemaFormatter:

    @classmethod
    def build_TableSchemaText(
        cls,
        table_name: str,
        table_schema: List[Dict[str, str]]
    ) -> str:
        lines = [f"Table: {table_name}", "Columns:"]

        for col in table_schema:
            name = col.get("COLUMN_NAME")
            dtype = cls._normalize_type(col)
            constraints = cls._extract_constraints(col)

            if constraints:
                lines.append(f"- {name} ({dtype}, {', '.join(constraints)})")
            else:
                lines.append(f"- {name} ({dtype})")

        return "\n".join(lines)

    @classmethod
    def build_DBSchemaText(cls,db_name:str,tables:List[Dict[str,str]])->str:
        txt = [f"Database : {db_name}","Tables :"]
        if not tables:
            print("None table returned")
            raise Exception("Got no tables, kindly generate tables ans run this function")
        for tab in tables:
            name = tab['TABLE_NAME']
            txt.append(f"- {name}")
        return "\n".join(txt)


    @classmethod
    def _normalize_type(cls, col: Dict[str, str]) -> str:
        dtype = col.get("DATA_TYPE", "").upper()

        if dtype in {"VARCHAR", "CHAR", "TEXT", "LONGTEXT", "MEDIUMTEXT"}:
            return "TEXT"

        if dtype in {"INT", "SMALLINT", "TINYINT"}:
            return "INT"

        if dtype in {"BIGINT"}:
            return "BIGINT"

        if dtype in {"DECIMAL", "NUMERIC", "FLOAT", "DOUBLE"}:
            return "DECIMAL"

        if dtype in {"DATETIME", "TIMESTAMP", "DATE"}:
            return "TIMESTAMP"

        if dtype == "JSON":
            return "JSON"

        if dtype == "ENUM":
            return cls._enum_values(col)

        return dtype

    @staticmethod
    def _enum_values(col: Dict[str, str]) -> str:
        column_type = col.get("COLUMN_TYPE", "")
        if column_type.lower().startswith("enum("):
            return f"ENUM{column_type[column_type.find('('):]}"
        return "ENUM"

    @staticmethod
    def _extract_constraints(col: Dict[str, str]) -> List[str]:
        constraints = []

        if col.get("COLUMN_KEY") == "PRI":
            constraints.append("PRIMARY KEY")

        if col.get("IS_NULLABLE") == "NO":
            constraints.append("NOT NULL")

        extra = col.get("EXTRA", "").upper()
        if "AUTO_INCREMENT" in extra:
            constraints.append("AUTO_INCREMENT")

        default = col.get("COLUMN_DEFAULT")
        if default is not None:
            if isinstance(default, str) and not default.upper().startswith("CURRENT_"):
                constraints.append(f"DEFAULT '{default}'")
            else:
                constraints.append(f"DEFAULT {default}")

        return constraints
