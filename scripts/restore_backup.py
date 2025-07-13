#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

CONFIG = {
    "DB_HOST": "mariadb",
    "DB_PORT": 3306,
    "DB_USER": "root",  # use root for DROP/CREATE access
    "DB_PASSWORD": "123",  # from docker-compose
    "DB_NAME": "_7ee1b10d24ab9a87",
    "SQL_FILE": "",  # optional: leave blank to auto-pick latest
}

BACKUP_DIR = "/home/frappe/frappe-bench/apps/erpnext/backups/git"

def get_latest_sql():
    sql_files = sorted(Path(BACKUP_DIR).glob("*.sql"), key=os.path.getmtime, reverse=True)
    return str(sql_files[0]) if sql_files else None

def restore_db(sql_file):
    print(f"🧨 Dropping old DB '{CONFIG['DB_NAME']}'...")
    subprocess.run([
        "mysql",
        f"-h{CONFIG['DB_HOST']}",
        f"-P{CONFIG['DB_PORT']}",
        f"-u{CONFIG['DB_USER']}",
        f"-p{CONFIG['DB_PASSWORD']}",
        "-e", f"DROP DATABASE IF EXISTS `{CONFIG['DB_NAME']}`;"
    ], check=True)

    print(f"🚧 Creating fresh DB '{CONFIG['DB_NAME']}'...")
    subprocess.run([
        "mysql",
        f"-h{CONFIG['DB_HOST']}",
        f"-P{CONFIG['DB_PORT']}",
        f"-u{CONFIG['DB_USER']}",
        f"-p{CONFIG['DB_PASSWORD']}",
        "-e", f"CREATE DATABASE `{CONFIG['DB_NAME']}`;"
    ], check=True)

    print(f"📦 Restoring SQL: {sql_file}")
    with open(sql_file, "rb") as f:
        subprocess.run([
            "mysql",
            f"-h{CONFIG['DB_HOST']}",
            f"-P{CONFIG['DB_PORT']}",
            f"-u{CONFIG['DB_USER']}",
            f"-p{CONFIG['DB_PASSWORD']}",
            CONFIG["DB_NAME"]
        ], stdin=f, check=True)

    print("✅ Restore complete.")

def main():
    sql_file = CONFIG["SQL_FILE"] or get_latest_sql()
    if not sql_file:
        print("❌ No SQL file found in backups/git/")
        return

    print(f"📁 Using SQL file: {sql_file}")
    restore_db(sql_file)

if __name__ == "__main__":
    main()
