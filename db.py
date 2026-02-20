import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        plan_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        duration_days INTEGER NOT NULL,
        points_multi REAL NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS boxes (
        month TEXT PRIMARY KEY,
        tea_name TEXT NOT NULL,
        tea_desc TEXT NOT NULL,
        bookmark_title TEXT NOT NULL,
        story_md TEXT NOT NULL,
        bookmark_img_path TEXT,
        qr_url TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_key TEXT PRIMARY KEY,
        plan_id TEXT NOT NULL,
        start_at TEXT NOT NULL,
        end_at TEXT NOT NULL,
        current_box_month TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    c.commit()
    seed_if_empty(c)
    c.close()


def seed_if_empty(c):
    cur = c.cursor()

    n = cur.execute("SELECT COUNT(*) AS n FROM plans").fetchone()["n"]
    if n == 0:
        cur.executemany(
            "INSERT INTO plans(plan_id,title,price,duration_days,points_multi) VALUES(?,?,?,?,?)",
            [
                ("month",  "月订", 29, 30, 1.0),
                ("season", "季订", 79, 90, 1.2),
                ("year",   "年订", 259, 365, 1.5),
            ]
        )

    m = cur.execute("SELECT COUNT(*) AS n FROM boxes").fetchone()["n"]
    if m == 0:
        cur.execute("""
        INSERT INTO boxes(month,tea_name,tea_desc,bookmark_title,story_md,bookmark_img_path,qr_url)
        VALUES(?,?,?,?,?,?,?)
        """, (
            "2026-02",
            "绿茶 · 日常清爽款",
            "清鲜｜豆香｜回甘（热泡/冷泡都适合）",
            "本月纹样书签：蝶影",
            "## 冲泡建议\n- 80–85℃\n- 2g茶：150ml水\n- 1–2分钟出汤\n\n## 纹样小故事\n蝶影象征轻盈与新生，适合做日常的微小仪式感。",
            None,
            None,
        ))
    c.commit()


def get_plans():
    c = conn()
    rows = c.execute("SELECT * FROM plans ORDER BY price ASC").fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_box(month: str):
    c = conn()
    row = c.execute("SELECT * FROM boxes WHERE month=?", (month,)).fetchone()
    c.close()
    return dict(row) if row else None


def list_boxes():
    c = conn()
    rows = c.execute("SELECT month, tea_name, bookmark_title FROM boxes ORDER BY month DESC").fetchall()
    c.close()
    return [dict(r) for r in rows]


def upsert_box(month, tea_name, tea_desc, bookmark_title, story_md, bookmark_img_path=None, qr_url=None):
    c = conn()
    c.execute("""
    INSERT INTO boxes(month, tea_name, tea_desc, bookmark_title, story_md, bookmark_img_path, qr_url)
    VALUES(?,?,?,?,?,?,?)
    ON CONFLICT(month) DO UPDATE SET
      tea_name=excluded.tea_name,
      tea_desc=excluded.tea_desc,
      bookmark_title=excluded.bookmark_title,
      story_md=excluded.story_md,
      bookmark_img_path=COALESCE(excluded.bookmark_img_path, boxes.bookmark_img_path),
      qr_url=COALESCE(excluded.qr_url, boxes.qr_url)
    """, (month, tea_name, tea_desc, bookmark_title, story_md, bookmark_img_path, qr_url))
    c.commit()
    c.close()


def set_subscription(user_key, plan_id, start_at, end_at, current_box_month, status="active"):
    c = conn()
    c.execute("""
    INSERT INTO subscriptions(user_key, plan_id, start_at, end_at, current_box_month, status)
    VALUES(?,?,?,?,?,?)
    ON CONFLICT(user_key) DO UPDATE SET
      plan_id=excluded.plan_id,
      start_at=excluded.start_at,
      end_at=excluded.end_at,
      current_box_month=excluded.current_box_month,
      status=excluded.status
    """, (user_key, plan_id, start_at, end_at, current_box_month, status))
    c.commit()
    c.close()


def get_subscription(user_key):
    c = conn()
    row = c.execute("SELECT * FROM subscriptions WHERE user_key=?", (user_key,)).fetchone()
    c.close()
    return dict(row) if row else None
