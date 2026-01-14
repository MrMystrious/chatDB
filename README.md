# ChatDB

**ChatDB** is an intelligent SQL query planning and execution assistant. It leverages Large Language Models (LLMs) to generate **safe, scalable, and executable SQL plans** from natural language queries. The system enforces **read-only, production-safe queries** and prevents unsafe operations such as `INSERT`, `DROP`, or use of temporary tables.

---

## Features

- **LLM-driven query planning**: Translate natural language queries into structured SQL execution steps.  
- **Step-wise decomposition**: Complex queries are split into ordered, executable steps.  
- **SQL safety enforcement**:
  - Only `SELECT` and `WITH SELECT` queries allowed
  - Blocks unsafe operations: `INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.
  - Prevents temporary tables and unbounded queries
- **AST-based validation**: Ensures semantic correctness of SQL (via `sqlglot`) rather than fragile regex.  
- **Dialect-aware**: MySQL-specific validation and SQL generation.
- **Safe execution engine**: Queries are executed on the database only after validation, never exposing large datasets in memory.

---

## Architecture

User Query (Natural Language)
│
▼
ChatDB Parser
│
▼
SQL Execution Plan (Step1, Step2...)
│
▼
ExecutionPlanValidator (AST Validation)
│
▼
Safe SQL Execution (MySQL)
│
▼
Aggregated / Summarized Result

yaml
Copy code

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-org/chatdb.git
cd chatdb
Create a virtual environment:
```
```bash
Copy code
python -m venv chatdb
```

# Activate environment:
## Linux / macOS
source chatdb/bin/activate

## Windows
chatdb\Scripts\activate
Install dependencies:

```bash
Copy code
pip install -r requirements.txt
```

## Requirements include:

mysql-connector-python – database connectivity

sqlglot – AST parsing for SQL validation

python-dotenv – environment variable support

Gemini SDK – LLM integration

## Configure environment variables:

Create a .env file:

env
Copy code
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=sakila
LLM_API_KEY=your_api_key
Usage
python
Copy code
from chatdb.init_user import User
from chatdb.chatDB import ChatQuery

# Initialize user with database connection and LLM model
user = User(api_key="YOUR_LLM_API_KEY")

query = ChatQuery(
    query="Count the number of films in each category.",
    model="gemini-3-flash-preview",
    base_prompt="You are ChatDB, an expert SQL query planner."
)

# Generate SQL execution plan and execute
```bash
response = user.chat(query)
print(response)
Example Output

Copy code
Step 1: Count films in each category.
`SELECT c.name, COUNT(fc.film_id) AS film_count
 FROM category AS c
 JOIN film_category AS fc ON c.category_id = fc.category_id
 GROUP BY c.name;`
```

# Development Notes

Parser: Extracts SQL steps from LLM output, handling backticks and triple backticks.

Validator: Checks step numbering, read-only enforcement, forbidden keywords, and TEMP table usage.

LLM Models: Tested with Gemini (3-pro, 3-flash) and GPT models. AST validation ensures SQL safety even if the LLM generates non-compliant SQL.

Extensibility: Rules for column whitelisting, LIMIT enforcement, or query cost analysis can be added easily.

##  Troubleshooting & Common Errors

| Error | Cause | Solution |
| :--- | :--- | :--- |
| **Only SELECT or WITH SELECT queries are allowed** | LLM returned a non-read-only SQL statement. | Adjust prompt or validator rules; enforce read-only queries. |
| **Expected exactly one SQL statement** | LLM output contained multiple statements in a single step. | Split SQL into separate steps; validate each separately. |
| **TEMP TABLE usage is forbidden** | LLM generated `CREATE TEMPORARY TABLE`. | Rewrite query using Common Table Expressions (CTEs) or subqueries. |