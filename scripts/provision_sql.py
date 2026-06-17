"""Provision MMC ops tables in Azure SQL from local CSVs.

Pattern A (Foundry IQ indexed Azure SQL knowledge source).

Connects via AAD bearer token (AzureCliCredential), creates one table per CSV
with simple type inference, bulk-loads rows, and enables change tracking on
the database + each table so the Foundry IQ indexer can do incremental updates.

Usage:
    .venv\\Scripts\\python.exe scripts\\provision_sql.py

Idempotent: drops + recreates each table.
"""

from __future__ import annotations

import csv
import logging
import os
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyodbc
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("provision_sql")

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")

SQL_FQDN = os.environ["SQL_SERVER_FQDN"]
SQL_DB = os.environ["SQL_DATABASE_NAME"]


@dataclass(frozen=True)
class TableSpec:
    name: str          # SQL table name (dbo.<name>)
    pk_col: str        # primary key column from CSV
    csv_path: Path     # source CSV (relative to repo root)


# Five tables (matches CSV files identified for SQL migration).
SPECS: list[TableSpec] = [
    TableSpec("training_log",   "Training_ID", REPO_ROOT / "plants/plant7/kb/08_Logs_Data/MMC_P7_Training_Log.csv"),
    TableSpec("pm_schedule",    "PM_ID",       REPO_ROOT / "plants/plant7/kb/08_Logs_Data/MMC_P7_PM_Schedule.csv"),
    TableSpec("incident_log",   "Incident_ID", REPO_ROOT / "plants/plant7/kb/08_Logs_Data/MMC_P7_Incident_Log.csv"),
    TableSpec("po_spend",       "PO_ID",       REPO_ROOT / "enterprise/procurement/data/po_spend.csv"),
    TableSpec("supplier_master","Supplier_ID", REPO_ROOT / "enterprise/supply-chain/data/supplier_master.csv"),
]


# --- AAD token connection (per docs.microsoft.com/azure/azure-sql/database/active-directory-interactive-connect-azure-sql-db) ---
SQL_COPT_SS_ACCESS_TOKEN = 1256  # mssql-specific connection attribute


def connect() -> pyodbc.Connection:
    """Open a pyodbc connection to Azure SQL using an AAD bearer token."""
    credential = AzureCliCredential()
    token = credential.get_token("https://database.windows.net/.default").token
    token_bytes = token.encode("utf-16-le")
    packed = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{SQL_FQDN},1433;"
        f"Database={SQL_DB};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: packed})


# --- Type inference (intentionally simple) ---
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
INT_RE = re.compile(r"^-?\d+$")
FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


def infer_type(values: list[str]) -> str:
    """Return a T-SQL type for a column given sample values (skipping blanks)."""
    samples = [v for v in values if v not in ("", None)]
    if not samples:
        return "NVARCHAR(MAX)"
    if all(DATE_RE.match(v) for v in samples):
        return "DATE"
    if all(TIME_RE.match(v) for v in samples):
        return "NVARCHAR(16)"  # keep as string; portable for CSV time-of-day
    if all(INT_RE.match(v) for v in samples):
        return "INT"
    if all(INT_RE.match(v) or FLOAT_RE.match(v) for v in samples):
        return "FLOAT"
    return "NVARCHAR(MAX)"


def quote_ident(name: str) -> str:
    """Safe T-SQL identifier (column / table) — strip non-word chars."""
    return "[" + re.sub(r"[^\w]", "_", name) + "]"


def cast_value(raw: str, sql_type: str) -> Any:
    """Convert a CSV string into the right Python type for pyodbc."""
    if raw in ("", None):
        return None
    if sql_type == "INT":
        return int(raw)
    if sql_type == "FLOAT":
        return float(raw)
    # DATE / NVARCHAR — let pyodbc handle strings (ODBC accepts YYYY-MM-DD literal for DATE).
    return raw


def load_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    return header, rows


def create_and_load(conn: pyodbc.Connection, spec: TableSpec) -> int:
    header, rows = load_csv(spec.csv_path)

    # Infer per-column type from first 50 rows.
    sample = rows[:50]
    col_types = [infer_type([r[i] if i < len(r) else "" for r in sample]) for i in range(len(header))]

    quoted_cols = [quote_ident(c) for c in header]
    col_defs = []
    for col, t, raw in zip(quoted_cols, col_types, header):
        if raw == spec.pk_col:
            # PK can't be NVARCHAR(MAX); cap to 450 (SQL Server key length limit).
            effective_type = "NVARCHAR(450)" if t == "NVARCHAR(MAX)" else t
            col_defs.append(f"{col} {effective_type} NOT NULL")
        else:
            col_defs.append(f"{col} {t} NULL")

    pk_quoted = quote_ident(spec.pk_col)
    create_sql = (
        f"CREATE TABLE dbo.{quote_ident(spec.name)} (\n  "
        + ",\n  ".join(col_defs)
        + f",\n  CONSTRAINT [PK_{spec.name}] PRIMARY KEY ({pk_quoted})\n);"
    )

    cur = conn.cursor()
    log.info("[%s] dropping if exists", spec.name)
    cur.execute(f"IF OBJECT_ID('dbo.{spec.name}','U') IS NOT NULL DROP TABLE dbo.{quote_ident(spec.name)};")
    log.info("[%s] creating (%d cols)", spec.name, len(header))
    cur.execute(create_sql)

    # Enable change tracking on the table (DB-level CT enabled separately).
    cur.execute(
        f"ALTER TABLE dbo.{quote_ident(spec.name)} "
        f"ENABLE CHANGE_TRACKING WITH (TRACK_COLUMNS_UPDATED = OFF);"
    )

    # Cast each row to typed values for INSERT.
    typed_rows = []
    for row in rows:
        padded = row + [""] * (len(header) - len(row))
        typed_rows.append(tuple(cast_value(padded[i], col_types[i]) for i in range(len(header))))

    placeholders = ",".join("?" * len(header))
    insert_sql = f"INSERT INTO dbo.{quote_ident(spec.name)} ({', '.join(quoted_cols)}) VALUES ({placeholders})"
    cur.fast_executemany = True
    cur.executemany(insert_sql, typed_rows)
    conn.commit()

    log.info("[%s] inserted %d rows", spec.name, len(typed_rows))
    return len(typed_rows)


def enable_db_change_tracking(conn: pyodbc.Connection) -> None:
    # ALTER DATABASE can't run inside a transaction; toggle autocommit briefly.
    prior = conn.autocommit
    conn.autocommit = True
    try:
        cur = conn.cursor()
        cur.execute(
            f"IF NOT EXISTS (SELECT 1 FROM sys.change_tracking_databases "
            f"WHERE database_id = DB_ID('{SQL_DB}')) "
            f"BEGIN ALTER DATABASE [{SQL_DB}] SET CHANGE_TRACKING = ON "
            f"(CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON); END"
        )
    finally:
        conn.autocommit = prior
    log.info("change tracking enabled on database %s", SQL_DB)


def main() -> int:
    log.info("connecting to %s / %s", SQL_FQDN, SQL_DB)
    conn = connect()
    try:
        enable_db_change_tracking(conn)
        total = 0
        for spec in SPECS:
            if not spec.csv_path.exists():
                log.warning("skip %s — CSV missing at %s", spec.name, spec.csv_path)
                continue
            total += create_and_load(conn, spec)
        log.info("done — %d total rows across %d tables", total, len(SPECS))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
