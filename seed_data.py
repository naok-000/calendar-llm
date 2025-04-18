import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta
import db_init

fake = Faker(['ja_JP'])

def seed_basic_data(conn, cursor):
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('bob', 'bob@example.com', 'hash2')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('carol', 'carol@example.com', 'hash3')")
    cursor.execute("INSERT OR IGNORE INTO categories (name, user_id) VALUES ('仕事', 1)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, user_id) VALUES ('プライベート', 2)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, user_id) VALUES ('勉強', 1)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, user_id) VALUES ('家族', 3)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, user_id) VALUES ('旅行', 2)")
    conn.commit()

def generate_random_users(cursor, count=20):
    for _ in range(count):
        username = fake.user_name()
        email = fake.email()
        password_hash = fake.sha256()
        try:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
        except sqlite3.IntegrityError:
            continue
    return [row[0] for row in cursor.execute("SELECT id FROM users").fetchall()]

def generate_random_categories(cursor, count=4):
    category_names = ['仕事', 'プライベート','家族',  '友人', ]
    for i in range(count):
        name = category_names[i]
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError:
            continue
    return [row[0] for row in cursor.execute("SELECT id FROM categories").fetchall()]

def generate_random_events(cursor, user_ids, category_ids, count=50):
    event_titles = ['会議', 'ミーティング', '打ち合わせ', 'ランチ', '勉強会', '映画鑑賞', '誕生日パーティー', 'デート', '買い物', '病院予約', '旅行', 'コンサート', '飲み会', '帰省', '講演会', 'セミナー', 'ワークショップ', '歯医者', '掃除', '洗濯', '料理', 'ジム', 'ヨガ']
    start_date = datetime.now() - timedelta(days=30)
    for _ in range(count):
        title = random.choice(event_titles)
        description = fake.paragraph(nb_sentences=2)
        event_date = start_date + timedelta(days=random.randint(0, 30))
        start_hour = random.randint(8, 20)
        duration_hours = random.randint(1, 3)
        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        owner_id = random.choice(user_ids)
        category_id = random.choice(category_ids)
        cursor.execute(
            "INSERT INTO events (title, description, start_datetime, end_datetime, owner_id, category_id) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, start_datetime, end_datetime, owner_id, category_id)
        )

def seed_large_dataset(db_path="calendar.db", user_count=20, event_count=100):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"ランダムユーザー {user_count} 件を生成中...")
    user_ids = generate_random_users(cursor, user_count)
    conn.commit()
    print("ランダムカテゴリーを生成中...")
    category_ids = generate_random_categories(cursor)
    conn.commit()
    print(f"ランダムイベント {event_count} 件を生成中...")
    generate_random_events(cursor, user_ids, category_ids, event_count)
    conn.commit()
    print("シードデータ投入完了！")
    conn.close()


if __name__ == "__main__":
    db_init.setup_database_structure()
    seed_large_dataset(user_count=10, event_count=200)