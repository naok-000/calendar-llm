import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta
import argparse

fake = Faker(['ja_JP'])

def seed_basic_data(conn, cursor):
    # ...既存の基本データ投入処理...
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hash1')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('bob', 'bob@example.com', 'hash2')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email, password_hash) VALUES ('carol', 'carol@example.com', 'hash3')")
    cursor.execute("INSERT OR IGNORE INTO categories (name, color, user_id) VALUES ('仕事', '#e74c3c', 1)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, color, user_id) VALUES ('プライベート', '#2ecc71', 2)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, color, user_id) VALUES ('勉強', '#3498db', 1)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, color, user_id) VALUES ('家族', '#9b59b6', 3)")
    cursor.execute("INSERT OR IGNORE INTO categories (name, color, user_id) VALUES ('旅行', '#f39c12', 2)")
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
    return cursor.execute("SELECT id FROM users").fetchall()

def generate_random_categories(cursor, user_ids, count=15):
    category_names = ['仕事', 'プライベート', '趣味', '勉強', '家族', '旅行', 'スポーツ', '読書', '音楽', '映画', '健康', '料理', 'ショッピング', '友人', 'プロジェクト']
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#9b59b6', '#f39c12', '#1abc9c', '#d35400', '#2c3e50', '#27ae60', '#8e44ad', '#c0392b', '#16a085', '#e67e22', '#2980b9', '#f1c40f']
    for _ in range(count):
        name = random.choice(category_names)
        color = random.choice(colors)
        user_id = random.choice(user_ids)[0]
        try:
            cursor.execute("INSERT INTO categories (name, color, user_id) VALUES (?, ?, ?)", (name, color, user_id))
        except sqlite3.IntegrityError:
            continue
    return cursor.execute("SELECT id FROM categories").fetchall()

def generate_random_events(cursor, user_ids, count=50):
    event_titles = ['会議', 'ミーティング', '打ち合わせ', 'ランチ', '勉強会', '映画鑑賞', '誕生日パーティー', 'デート', '買い物', '病院予約', '旅行', 'コンサート', '飲み会', '帰省', '講演会', 'セミナー', 'ワークショップ', '歯医者', '掃除', '洗濯', '料理', 'ジム', 'ヨガ']
    locations = ['会議室A', '会議室B', 'カフェ', 'レストラン', '自宅', '公園', '映画館', 'ショッピングモール', '駅', '病院', 'ホテル', 'ジム', '美術館', '図書館']
    start_date = datetime.now() - timedelta(days=30)
    for _ in range(count):
        title = random.choice(event_titles)
        description = fake.paragraph(nb_sentences=2)
        event_date = start_date + timedelta(days=random.randint(0, 60))
        start_hour = random.randint(8, 20)
        duration_hours = random.randint(1, 3)
        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        location = random.choice(locations)
        is_all_day = 1 if random.random() < 0.2 else 0
        owner_id = random.choice(user_ids)[0]
        is_public = 1 if random.random() < 0.7 else 0
        cursor.execute("INSERT INTO events (title, description, start_datetime, end_datetime, location, is_all_day, owner_id, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, description, start_datetime, end_datetime, location, is_all_day, owner_id, is_public))
    return cursor.execute("SELECT id FROM events").fetchall()

def generate_event_categories(cursor, event_ids, category_ids, count=60):
    for _ in range(count):
        event_id = random.choice(event_ids)[0]
        category_id = random.choice(category_ids)[0]
        try:
            cursor.execute("INSERT INTO event_categories (event_id, category_id) VALUES (?, ?)", (event_id, category_id))
        except sqlite3.IntegrityError:
            continue

def generate_reminders(cursor, event_ids, count=40):
    for _ in range(count):
        event_id = random.choice(event_ids)[0]
        event_start = cursor.execute("SELECT start_datetime FROM events WHERE id = ?", (event_id,)).fetchone()[0]
        if isinstance(event_start, str):
            event_start = datetime.fromisoformat(event_start.replace(' ', 'T'))
        reminder_minutes = random.choice([5, 10, 15, 30, 60])
        reminder_time = event_start - timedelta(minutes=reminder_minutes)
        cursor.execute("INSERT INTO reminders (event_id, reminder_time) VALUES (?, ?)", (event_id, reminder_time))

def generate_event_shares(cursor, event_ids, user_ids, count=30):
    for _ in range(count):
        event_id = random.choice(event_ids)[0]
        owner_id = cursor.execute("SELECT owner_id FROM events WHERE id = ?", (event_id,)).fetchone()[0]
        available_users = [user[0] for user in user_ids if user[0] != owner_id]
        if not available_users:
            continue
        user_id = random.choice(available_users)
        permission = random.choice(['view', 'edit'])
        try:
            cursor.execute("INSERT INTO event_shares (event_id, user_id, permission) VALUES (?, ?, ?)", (event_id, user_id, permission))
        except sqlite3.IntegrityError:
            continue

def seed_large_dataset(db_path="calendar.db", user_count=20, event_count=100):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("基本シードデータを投入中...")
    seed_basic_data(conn, cursor)
    print(f"ランダムユーザー {user_count} 件を生成中...")
    user_ids = generate_random_users(cursor, user_count)
    conn.commit()
    print("ランダムカテゴリーを生成中...")
    category_ids = generate_random_categories(cursor, user_ids)
    conn.commit()
    print(f"ランダムイベント {event_count} 件を生成中...")
    event_ids = generate_random_events(cursor, user_ids, event_count)
    conn.commit()
    print("イベント・カテゴリー紐付けを生成中...")
    generate_event_categories(cursor, event_ids, category_ids)
    conn.commit()
    print("リマインダーを生成中...")
    generate_reminders(cursor, event_ids)
    conn.commit()
    print("イベント共有データを生成中...")
    generate_event_shares(cursor, event_ids, user_ids)
    conn.commit()
    print("大量シードデータ投入完了！")
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--basic", action="store_true", help="最小限のサンプルデータのみ投入")
    parser.add_argument("--users", type=int, default=20)
    parser.add_argument("--events", type=int, default=100)
    args = parser.parse_args()

    if args.basic:
        conn = sqlite3.connect("calendar.db")
        cursor = conn.cursor()
        seed_basic_data(conn, cursor)
        conn.close()
        print("最小限のサンプルデータを投入しました。")
    else:
        seed_large_dataset(user_count=args.users, event_count=args.events)

if __name__ == "__main__":
    main()
