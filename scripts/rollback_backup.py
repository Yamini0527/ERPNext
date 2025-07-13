#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

CONFIG = {
    "GIT_REPO_PATH": "/home/frappe/frappe-bench/apps/erpnext",
    "SQL_RELATIVE_PATH": "backups/git",
    "DB_HOST": "mariadb",
    "DB_PORT": 3306,
    "DB_USER": "root",                     # root for DROP/CREATE
    "DB_PASSWORD": "123",                 # from docker-compose
    "DB_NAME": "_7ee1b10d24ab9a87",       # from site_config.json
}

def run_cmd(cmd, **kwargs):
    print(f"🔧 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kwargs)

def restore_sql(sql_path):
    print(f"📦 Restoring from: {sql_path}")

    run_cmd([
        "mysql",
        f"-h{CONFIG['DB_HOST']}",
        f"-P{CONFIG['DB_PORT']}",
        f"-u{CONFIG['DB_USER']}",
        f"-p{CONFIG['DB_PASSWORD']}",
        "-e", f"DROP DATABASE IF EXISTS `{CONFIG['DB_NAME']}`;"
    ])

    run_cmd([
        "mysql",
        f"-h{CONFIG['DB_HOST']}",
        f"-P{CONFIG['DB_PORT']}",
        f"-u{CONFIG['DB_USER']}",
        f"-p{CONFIG['DB_PASSWORD']}",
        "-e", f"CREATE DATABASE `{CONFIG['DB_NAME']}`;"
    ])

    with open(sql_path, 'rb') as f:
        run_cmd([
            "mysql",
            f"-h{CONFIG['DB_HOST']}",
            f"-P{CONFIG['DB_PORT']}",
            f"-u{CONFIG['DB_USER']}",
            f"-p{CONFIG['DB_PASSWORD']}",
            CONFIG["DB_NAME"]
        ] + ([] if sql_path.endswith(".sql") else ["--binary-mode"]), stdin=f)

    print("✅ Rollback complete.")

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 rollback_backup.py <commit_hash>")
        sys.exit(1)

    commit = sys.argv[1]
    os.chdir(CONFIG["GIT_REPO_PATH"])

    rel_path = CONFIG["SQL_RELATIVE_PATH"]
    print(f"🔁 Checking out backup at commit: {commit}")
    run_cmd(["git", "checkout", commit, "--", rel_path])

    full_path = os.path.join(CONFIG["GIT_REPO_PATH"], rel_path)
    sql_files = list(Path(full_path).glob("*.sql"))
    if not sql_files:
        print("❌ No .sql file found in checked out commit.")
        sys.exit(1)

    restore_sql(str(sql_files[0]))

if __name__ == "__main__":
    main()
