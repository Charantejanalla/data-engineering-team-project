import argparse
import ast
import json
import os
from pathlib import Path
import sqlite3
import tempfile

import pandas as pd


def extract(source_dir):
    """Read SQLite tables and CSV files without modifying the inputs."""
    db = source_dir / "PerfectPetClub.db"
    tables = {}

    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as source:
        if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Source database failed its integrity check")

        if source.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Source database contains invalid foreign keys")

        names = source.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()

        for (name,) in names:
            quoted = '"' + name.replace('"', '""') + '"'
            tables[name] = pd.read_sql_query(
                "SELECT * FROM " + quoted, source
            )

    # Credentials are unnecessary for analytics.
    tables["customer"] = tables["customer"].drop(
        columns=["password_hash"]
    )

    tables["crm_contact"] = pd.read_csv(
        source_dir / "PerfectPetClub_CRM_report.csv",
        dtype="string",
    )
    tables["server_event"] = pd.read_csv(
        source_dir / "PerfectPetClub_server_log.csv",
        dtype="string",
    )
    return tables
