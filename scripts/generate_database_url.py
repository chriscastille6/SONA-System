#!/usr/bin/env python3
"""
Generate a DATABASE_URL line for .env using the password in ~/hsirb-db-password.txt.
Run on the server: python scripts/generate_database_url.py
Then paste the output into ~/hsirb-system/.env (as DATABASE_URL=...).
"""
import os
from urllib.parse import quote_plus

DEFAULT_PASSWORD_FILE = os.path.expanduser("~/hsirb-db-password.txt")
DB_USER = "hsirb_user"
DB_NAME = "hsirb_db"
HOST = "localhost"
PORT = "5432"


def main():
    path = os.environ.get("HSIRB_DB_PASSWORD_FILE", DEFAULT_PASSWORD_FILE)
    if not os.path.isfile(path):
        print(f"Password file not found: {path}", file=os.sys.stderr)
        os.sys.exit(1)
    with open(path) as f:
        password = f.read().strip()
    encoded = quote_plus(password)
    url = f"postgresql://{DB_USER}:{encoded}@{HOST}:{PORT}/{DB_NAME}"
    print(f"DATABASE_URL={url}")


if __name__ == "__main__":
    main()
