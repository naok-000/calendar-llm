import getpass
import os
from langchain_community.utilities import SQLDatabase
import sqlite3
import seed_data


def setup_database_structure():
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()
    # 既存のテーブル作成処理
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        start_datetime DATETIME NOT NULL,
        end_datetime DATETIME,
        location TEXT,
        is_all_day BOOLEAN DEFAULT 0,
        owner_id INTEGER NOT NULL,
        is_public BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#3498db',
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_categories (
        event_id INTEGER,
        category_id INTEGER,
        PRIMARY KEY (event_id, category_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        reminder_time DATETIME NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_shares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        permission TEXT CHECK(permission IN ('view', 'edit')) DEFAULT 'view',
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(event_id, user_id)
    )''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database_structure()
    print("\nデータ生成オプション:")
    print("1: 最小限のサンプルデータのみ")
    print("2: 大量のランダムデータ (デフォルト: ユーザー20件、イベント100件)")
    print("3: カスタム量のランダムデータ")
    choice = input("選択してください (1-3): ")
    if choice == "1":
        print("最小限のサンプルデータを投入中...")
        conn = sqlite3.connect("calendar.db")
        cursor = conn.cursor()
        seed_data.seed_basic_data(conn, cursor)
        conn.close()
    elif choice == "3":
        user_count = int(input("生成するユーザー数: "))
        event_count = int(input("生成するイベント数: "))
        print(f"カスタム量のデータを生成: ユーザー {user_count}件、イベント {event_count}件")
        seed_data.seed_large_dataset(user_count=user_count, event_count=event_count)
    else:
        print("デフォルト量のランダムデータを生成中...")
        seed_data.seed_large_dataset()
    print("データベースセットアップ完了!")

# DB connection string
db = SQLDatabase.from_uri("sqlite:///calendar.db", sample_rows_in_table_info=3)
