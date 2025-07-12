import os
import subprocess
import datetime
import shutil
import gzip
from pathlib import Path

CONFIG = {
    "DB_HOST": "mariadb",                 # from docker-compose
    "DB_PORT": 3306,
    "DB_USER": "_7ee1b10d24ab9a87",                    # default ERPNext DB user
    "DB_PASSWORD": "FrHp1CnGMe9DUk1d",                 # from docker-compose.yml
    "DB_NAME": "_7ee1b10d24ab9a87",       # from site_config.json

    "FRAPPE_BENCH_PATH": "/frappe-bench",                         # ✅ if needed for rollback/git
    "SITE_NAME": "erpnext.localhost",

    "BACKUP_DIR": "/frappe-bench/apps/erpnext/backups",           # ✅ your chosen path
    "GIT_REPO_PATH": "/frappe-bench/apps/erpnext/backups/git",    # ✅ Git-tracked folder
    "GIT_ENABLED": True,
    "COMPRESS_BACKUPS": True
}

def create_backup_dir():
    try:
        Path(CONFIG["BACKUP_DIR"]).mkdir(parents=True, exist_ok=True)
        Path(CONFIG["GIT_REPO_PATH"]).mkdir(parents=True, exist_ok=True)
        if CONFIG["GIT_ENABLED"]:
            os.chdir(CONFIG["GIT_REPO_PATH"])
            if not Path(".git").exists():
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "config", "user.name", "ERPNext Backup"], check=True)
                subprocess.run(["git", "config", "user.email", "backup@erpnext.com"], check=True)
                with open(".gitignore", "w") as f:
                    f.write("*.gz\n*.zip\n*.tar\n")
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
        return
    try:
        dest = os.path.join(CONFIG["GIT_REPO_PATH"], os.path.basename(backup_path).replace(".gz", ".sql"))
        print(f"📁 Copying to Git folder: {dest}")
        subprocess.run(["gzip", "-d", backup_path], check=True)  # decompress before git commit
        shutil.move(backup_path.replace(".gz", ""), dest)

        os.chdir(CONFIG["GIT_REPO_PATH"])
        subprocess.run(["git", "add", "."], check=True)
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
        print("🔁 Step 4: Committing SQL to Git...")
        git_commit(sql_file)

    print("✅ Step 5: Backup process completed!")

if __name__ == "__main__":
    main()