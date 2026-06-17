"""Grant Foundry IQ Search service managed identities access to the SQL DB.

Run AFTER provision_sql.py. Creates an Entra-backed contained user for each
Search service MI and grants db_datareader (enough for indexers to pull rows).
"""

from __future__ import annotations

import logging
import os
import struct
import sys
from pathlib import Path

import pyodbc
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("grant_sql_access")

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

SQL_FQDN = os.environ["SQL_SERVER_FQDN"]
SQL_DB = os.environ["SQL_DATABASE_NAME"]

# (display_name_in_sql, MI object id) — Search service MIs that need read access.
PRINCIPALS = [
    ("srch-mmc-plant", "<search-plant-mi-object-id>"),
    ("srch-mmc-enterprise", "<search-enterprise-mi-object-id>"),
]

SQL_COPT_SS_ACCESS_TOKEN = 1256


def connect() -> pyodbc.Connection:
    token = AzureCliCredential().get_token("https://database.windows.net/.default").token
    tb = token.encode("utf-16-le")
    packed = struct.pack(f"<I{len(tb)}s", len(tb), tb)
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{SQL_FQDN},1433;"
        f"Database={SQL_DB};"
        "Encrypt=yes;"
    )
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: packed})


def grant(conn: pyodbc.Connection, name: str, object_id: str) -> None:
    cur = conn.cursor()
    # Create contained user from the MI (idempotent — DROP first if exists).
    cur.execute(f"IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'{name}') DROP USER [{name}];")
    cur.execute(f"CREATE USER [{name}] FROM EXTERNAL PROVIDER WITH OBJECT_ID = '{object_id}';")
    cur.execute(f"ALTER ROLE db_datareader ADD MEMBER [{name}];")
    # IndexedSqlKnowledgeSource also needs VIEW CHANGE TRACKING for incremental.
    cur.execute(f"GRANT VIEW CHANGE TRACKING ON SCHEMA::dbo TO [{name}];")
    conn.commit()
    log.info("granted db_datareader + VIEW CHANGE TRACKING to %s (oid=%s)", name, object_id)


def main() -> int:
    log.info("connecting to %s / %s", SQL_FQDN, SQL_DB)
    conn = connect()
    try:
        for name, oid in PRINCIPALS:
            grant(conn, name, oid)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
