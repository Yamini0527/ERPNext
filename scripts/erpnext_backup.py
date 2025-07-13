import os
import subprocess
import datetime
import shutil
import gzip
from pathlib import Path

CONFIG = {
    "DB_HOST": "mariadb",
    "DB_PORT": 3306,
    "DB_USER": "_4341c3e98369b05e",
    "DB_PASSWORD": "F2OmTSIyLswAKhn4",
    "DB_NAME": "_4341c3e98369b05e",

    "FRAPPE_BENCH_PATH": "/home/frappe/frappe-bench/apps/erpnext",
    "SITE_NAME": "erpnext.localhost",

    "BACKUP_DIR": "/home/frappe/frappe-bench/apps/erpnext/backups",
    "GIT_REPO_PATH": "/home/frappe/frappe-bench/apps/erpnext/backups/git",
    "GIT_ENABLED": False,  # set to False to prevent auto-commit
    "COMPRESS_BACKUPS": True
}


def create_backup_dir():
    try:
        Path(CONFIG["BACKUP_DIR"]).mkdir(parents=True, exist_ok=True)
        Path(CONFIG["GIT_REPO_PATH"]).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating backup or git directories: {e}")


def run_mysqldump(backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"db_backup_{timestamp}.sql"
    filepath = os.path.join(backup_dir, filename)

    cmd = [
        "mysqldump",
        f"--host={CONFIG['DB_HOST']}",
        f"--port={CONFIG['DB_PORT']}",
        f"--user={CONFIG['DB_USER']}",
        f"--password={CONFIG['DB_PASSWORD']}",
        "--single-transaction",
        CONFIG["DB_NAME"]
    ]

    try:
        print(f"📦 Running mysqldump...")
        with open(filepath, "wb") as f:
            subprocess.run(cmd, stdout=f, check=True)
        print(f"✅ Dump created: {filepath}")

        if CONFIG["COMPRESS_BACKUPS"]:
            print(f"🗜 Compressing backup...")
            with open(filepath, 'rb') as f_in, gzip.open(f"{filepath}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(filepath)
            filepath += ".gz"
            print(f"✅ Compressed: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error during mysqldump: {e}")
        return None


def git_commit(backup_path):
    if not CONFIG["GIT_ENABLED"] or not backup_path:
        print("🔕 Git auto-commit disabled. You can commit manually.")
        return
    try:
        subprocess.run(["gzip", "-d", backup_path], check=True)
        sql_path = backup_path.replace(".gz", "")
        dest = os.path.join(CONFIG["GIT_REPO_PATH"], Path(sql_path).name)
        shutil.move(sql_path, dest)

        os.chdir(CONFIG["FRAPPE_BENCH_PATH"])
        subprocess.run(["git", "add", dest], check=True)
        commit_msg = f"Backup {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("🎉 Git commit complete.")
    except Exception as e:
        print(f"❌ Git commit failed: {e}")


def main():
    print("🛠 Step 1: Creating backup directories...")
    create_backup_dir()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(CONFIG["BACKUP_DIR"], f"full_backup_{timestamp}")
    print(f"📁 Step 2: Creating backup folder: {backup_folder}")
    Path(backup_folder).mkdir(parents=True, exist_ok=True)

    print("📦 Step 3: Running DB dump...")
    sql_file = run_mysqldump(backup_folder)

    if sql_file:
        print("🔁 Step 4: Preparing Git commit (manual)...")
        git_commit(sql_file)

    print("✅ Step 5: Backup process completed!")


if __name__ == "__main__":
    main()
