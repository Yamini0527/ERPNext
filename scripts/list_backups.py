import subprocess

def list_backups():
    print("📜 Listing backups committed to Git...\n")

    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h %ad %s", "--date=short", "--", "backups/git/*.sql"],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout:
            print(result.stdout)
        else:
            print("⚠️ No committed SQL backups found.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git log failed: {e}")

if __name__ == "__main__":
    list_backups()
