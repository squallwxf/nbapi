import argparse
import os
import sqlite3
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("NBAPI_DB_PATH", str(ROOT / "nbapi.sqlite3"))).expanduser()
BACKUP_DIR = Path(os.environ.get("NBAPI_BACKUP_DIR", str(ROOT / "backups"))).expanduser()


def make_backup(target: Path | None = None) -> Path:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"database not found: {DB_PATH}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if target is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = BACKUP_DIR / f"nbapi-{stamp}.sqlite3"
    with sqlite3.connect(DB_PATH) as source, sqlite3.connect(target) as dest:
        source.backup(dest)
    return target


def main():
    parser = argparse.ArgumentParser(description="Backup NBAPI SQLite database.")
    parser.add_argument("--output", type=Path, help="Optional backup file path.")
    args = parser.parse_args()
    backup_path = make_backup(args.output)
    print(backup_path)


if __name__ == "__main__":
    main()
