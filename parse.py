import re
from typing import List, Dict

class ExecutionPlanError(Exception):
    pass

class ExecutionPlanValidator:
    _FORBIDDEN_SQL = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE)\b",
        re.IGNORECASE
    )

    _READ_ONLY = re.compile(
        r"^\s*(SELECT|WITH)\b",
        re.IGNORECASE
    )

    _FORBIDDEN_TEMP = re.compile(
        r"\bTEMP\b|\bCREATE\b",
        re.IGNORECASE
    )

    @classmethod
    def _normalize_sql(cls, sql: str) -> str:
        sql = sql.strip()

        if sql.startswith("```"):
            sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
            sql = re.sub(r"\s*```$", "", sql)

        if sql.startswith("`") and sql.endswith("`"):
            sql = sql[1:-1]

        return sql.strip()

    @classmethod
    def validate(cls, steps: list[dict]) -> None:
        if not steps:
            raise ExecutionPlanError("No execution steps found")

        expected_step = 1

        for step in steps:
            if step.get("step_number") != expected_step:
                raise ExecutionPlanError(
                    f"Step numbering invalid: expected Step{expected_step}"
                )

            raw_sql = step.get("sql", "")
            if not raw_sql or not isinstance(raw_sql, str):
                raise ExecutionPlanError(
                    f"Empty or missing SQL in Step{expected_step}"
                )

            sql = cls._normalize_sql(raw_sql)

            # Enforce read-only
            if not cls._READ_ONLY.match(sql):
                raise ExecutionPlanError(
                    f"Only SELECT or WITH SELECT queries are allowed (Step{expected_step})"
                )

            # Block temp / create
            if cls._FORBIDDEN_TEMP.search(sql):
                raise ExecutionPlanError(
                    f"TEMP TABLE usage is forbidden (Step{expected_step})"
                )

            # Enforce single statement
            sql = sql.rstrip(";")
            statements = [s for s in sql.split(";") if s.strip()]
            if len(statements) != 1:
                raise ExecutionPlanError(
                    f"Expected exactly one SQL statement in Step{expected_step}, "
                    f"found {len(statements)}"
                )

            # Block unsafe ops
            if cls._FORBIDDEN_SQL.search(sql):
                raise ExecutionPlanError(
                    f"Unsafe SQL operation detected in Step{expected_step}"
                )

            expected_step += 1

class Parser:
    @classmethod
    def parseResponse(cls, response: str) -> List[Dict[str, str]]:
        pattern = re.compile(
            r"Step\s*(\d+)\s*:\s*(.*?)\s*`([\s\S]*?)`",
            re.IGNORECASE
        )

        result = []
        for match in pattern.finditer(response):
            result.append({
                "step_number": int(match.group(1)),
                "description": match.group(2).strip(),
                "sql": match.group(3).strip()
            })

        ExecutionPlanValidator.validate(result)
        return result
