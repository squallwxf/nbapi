import hashlib
import json
import secrets
import sqlite3
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "nbapi.sqlite3"
HTML_PATH = ROOT / "api-website.html"
UPSTREAM = "https://ai.krapi.cn"
MICROS_PER_DOLLAR = 1_000_000
TOKEN_PREFIX = "nb_sk_"

MODEL_ROWS = [
    ("T香蕉2", "Gemini 图片", "Google", "图片生成", "per_task", 100000),
    ("T香蕉pro", "Gemini 图片", "Google", "图片生成", "per_task", 100000),
    ("gpt-5.5", "GPT 5.5", "OpenAI", "对话模型", "per_token", 0),
    ("gpt-5.6-sol", "GPT 5.6 Sol", "OpenAI", "对话模型", "per_token", 0),
    ("gpt-5.6-terra", "GPT 5.6 Terra", "OpenAI", "对话模型", "per_token", 0),
    ("gpt-image-2", "GPT 图片", "OpenAI", "图片生成", "per_task", 100000),
    ("grok-video-480p", "Grok 视频", "Grok", "视频生成", "per_task", 500000),
    ("grok-video-720p", "Grok 视频", "Grok", "视频生成", "per_task", 500000),
    ("grok-imagine-video-1.5-480p", "Grok 1.5 视频", "Grok", "视频生成", "per_task", 500000),
    ("grok-imagine-video-1.5-720p", "Grok 1.5 视频", "Grok", "视频生成", "per_task", 500000),
    ("omni-flash", "Omni 视频", "Omni", "视频生成", "per_task", 500000),
    ("omni-flash-1080p", "Omni 视频", "Omni", "视频生成", "per_task", 500000),
    ("omni-flash-4k", "Omni 视频", "Omni", "视频生成", "per_task", 500000),
    ("omni-flash-components", "Omni 视频", "Omni", "参考图生视频", "per_task", 500000),
    ("omni-flash-components-1080p", "Omni 视频", "Omni", "参考图生视频", "per_task", 500000),
    ("omni-flash-components-4k", "Omni 视频", "Omni", "参考图生视频", "per_task", 500000),
    ("omni-flash-edit", "Omni 视频编辑", "Omni", "视频编辑", "per_task", 500000),
    ("omni-flash-edit-1080p", "Omni 视频编辑", "Omni", "视频编辑", "per_task", 500000),
    ("omni-flash-edit-4k", "Omni 视频编辑", "Omni", "视频编辑", "per_task", 500000),
    ("sora-v3-fast", "Sora 视频", "Sora / Veo", "文生视频", "per_task", 500000),
    ("sora-v3-fast-1080p", "Sora 视频", "Sora / Veo", "文生视频", "per_task", 500000),
    ("sora-v3-pro", "Sora 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("sora-v3-pro-1080p", "Sora 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-lite-720", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-lite-1080", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-lite-4k", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-fast-720", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-fast-1080", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-fast-4k", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-quality-720", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-quality-1080", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
    ("veo-3.1-quality-4k", "Veo 视频", "Sora / Veo", "视频生成", "per_task", 500000),
]


def now() -> int:
    return int(time.time())


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
        return secrets.compare_digest(actual, expected)
    except ValueError:
        return False


def dollars_to_micros(value) -> int:
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError("price must be a valid number")
    if amount < 0 or amount > Decimal("1000000"):
        raise ValueError("price is out of range")
    return int(amount * MICROS_PER_DOLLAR)


def micros_to_dollars(value: int) -> str:
    return f"{Decimal(value) / MICROS_PER_DOLLAR:.6f}"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(
            """
            PRAGMA journal_mode = WAL;
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
              balance_micros INTEGER NOT NULL DEFAULT 0,
              created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL REFERENCES users(id),
              expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS api_tokens (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              name TEXT NOT NULL,
              token_hash TEXT NOT NULL UNIQUE,
              token_hint TEXT NOT NULL,
              active INTEGER NOT NULL DEFAULT 1,
              created_at INTEGER NOT NULL,
              last_used_at INTEGER,
              expires_at INTEGER
            );
            CREATE TABLE IF NOT EXISTS models (
              name TEXT PRIMARY KEY,
              provider_label TEXT NOT NULL,
              provider TEXT NOT NULL,
              kind TEXT NOT NULL,
              billing_unit TEXT NOT NULL CHECK(billing_unit IN ('per_task', 'per_token')),
              price_micros INTEGER NOT NULL,
              active INTEGER NOT NULL DEFAULT 1,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ledger (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              model_name TEXT NOT NULL REFERENCES models(name),
              idempotency_key TEXT NOT NULL,
              amount_micros INTEGER NOT NULL,
              billing_unit TEXT NOT NULL,
              input_tokens INTEGER NOT NULL DEFAULT 0,
              output_tokens INTEGER NOT NULL DEFAULT 0,
              status TEXT NOT NULL CHECK(status IN ('charged', 'refunded')),
              created_at INTEGER NOT NULL,
              UNIQUE(user_id, idempotency_key)
            );
            """
        )
        columns = {row[1] for row in db.execute("PRAGMA table_info(ledger)")}
        if "token_id" not in columns:
            db.execute("ALTER TABLE ledger ADD COLUMN token_id INTEGER REFERENCES api_tokens(id)")
        timestamp = now()
        db.execute(
            "INSERT OR IGNORE INTO users(username, password_hash, role, balance_micros, created_at) VALUES (?, ?, 'admin', ?, ?)",
            ("admin", hash_password("admin123"), 100 * MICROS_PER_DOLLAR, timestamp),
        )
        db.execute(
            "INSERT OR IGNORE INTO users(username, password_hash, role, balance_micros, created_at) VALUES (?, ?, 'user', ?, ?)",
            ("demo", hash_password("demo123"), 100 * MICROS_PER_DOLLAR, timestamp),
        )
        for name, provider_label, provider, kind, billing_unit, price_micros in MODEL_ROWS:
            db.execute(
                """INSERT OR IGNORE INTO models
                (name, provider_label, provider, kind, billing_unit, price_micros, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, provider_label, provider, kind, billing_unit, price_micros, timestamp),
            )


def json_bytes(payload) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "NBAPI/1.0"

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_json(self, status: int, payload) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 2_000_000:
            raise ValueError("request body too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def current_user(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:].strip()
        with sqlite3.connect(DB_PATH) as db:
            return db.execute(
                """SELECT u.id, u.username, u.role, u.balance_micros
                   FROM sessions s JOIN users u ON u.id=s.user_id
                   WHERE s.token=? AND s.expires_at>?""",
                (token, now()),
            ).fetchone()

    def require_user(self, admin=False):
        user = self.current_user()
        if not user:
            self.send_json(401, {"error": "authentication_required"})
            return None
        if admin and user[2] != "admin":
            self.send_json(403, {"error": "admin_required"})
            return None
        return user

    def require_api_token(self):
        header = self.headers.get("X-NBAPI-Key", "").strip()
        if not header:
            authorization = self.headers.get("Authorization", "").strip()
            if authorization.startswith("Bearer nb_sk_"):
                header = authorization[7:].strip()
        if not header.startswith(TOKEN_PREFIX):
            self.send_json(401, {"error": "api_key_required"})
            return None
        token_hash = hashlib.sha256(header.encode("utf-8")).hexdigest()
        with sqlite3.connect(DB_PATH) as db:
            row = db.execute(
                """SELECT t.id, t.user_id, u.username, u.role, u.balance_micros
                   FROM api_tokens t JOIN users u ON u.id=t.user_id
                   WHERE t.token_hash=? AND t.active=1
                     AND (t.expires_at IS NULL OR t.expires_at>?)""",
                (token_hash, now()),
            ).fetchone()
            if row:
                db.execute("UPDATE api_tokens SET last_used_at=? WHERE id=?", (now(), row[0]))
        if not row:
            self.send_json(401, {"error": "invalid_or_inactive_api_key"})
            return None
        return row

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Idempotency-Key")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/models":
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute("SELECT name, provider_label, provider, kind, billing_unit, price_micros, active FROM models ORDER BY rowid").fetchall()
            self.send_json(200, {"models": [
                {"name": r[0], "providerLabel": r[1], "provider": r[2], "kind": r[3], "billingUnit": r[4], "price": micros_to_dollars(r[5]), "active": bool(r[6])}
                for r in rows
            ]})
            return
        if path == "/api/me":
            user = self.require_user()
            if user:
                self.send_json(200, {"id": user[0], "username": user[1], "role": user[2], "balance": micros_to_dollars(user[3])})
            return
        if path == "/api/ledger":
            user = self.require_user()
            if user:
                with sqlite3.connect(DB_PATH) as db:
                    rows = db.execute("SELECT model_name, amount_micros, billing_unit, input_tokens, output_tokens, status, created_at FROM ledger WHERE user_id=? ORDER BY id DESC LIMIT 100", (user[0],)).fetchall()
                self.send_json(200, {"items": [{"model": r[0], "amount": micros_to_dollars(r[1]), "billingUnit": r[2], "inputTokens": r[3], "outputTokens": r[4], "status": r[5], "createdAt": r[6]} for r in rows]})
            return
        if path == "/api/tokens":
            user = self.require_user()
            if user:
                with sqlite3.connect(DB_PATH) as db:
                    rows = db.execute(
                        "SELECT id, name, token_hint, active, created_at, last_used_at, expires_at FROM api_tokens WHERE user_id=? ORDER BY id DESC",
                        (user[0],),
                    ).fetchall()
                self.send_json(200, {"items": [{
                    "id": r[0], "name": r[1], "hint": r[2], "active": bool(r[3]),
                    "createdAt": r[4], "lastUsedAt": r[5], "expiresAt": r[6]
                } for r in rows]})
            return
        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            body = HTML_PATH.read_bytes()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return

        if path == "/api/auth/login":
            username = str(payload.get("username", "")).strip()
            password = str(payload.get("password", ""))
            with sqlite3.connect(DB_PATH) as db:
                row = db.execute("SELECT id, username, password_hash, role, balance_micros FROM users WHERE username=?", (username,)).fetchone()
                if not row or not verify_password(password, row[2]):
                    self.send_json(401, {"error": "invalid_credentials"})
                    return
                token = secrets.token_urlsafe(32)
                db.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)", (token, row[0], now() + 7 * 86400))
            self.send_json(200, {"token": token, "user": {"id": row[0], "username": row[1], "role": row[3], "balance": micros_to_dollars(row[4])}})
            return

        if path == "/api/tokens":
            user = self.require_user()
            if not user:
                return
            name = str(payload.get("name", "")).strip() or "未命名令牌"
            if len(name) > 64:
                self.send_json(400, {"error": "token_name_too_long"})
                return
            raw_token = TOKEN_PREFIX + secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            token_hint = f"{raw_token[:12]}********{raw_token[-4:]}"
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute(
                    "INSERT INTO api_tokens(user_id, name, token_hash, token_hint, active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                    (user[0], name, token_hash, token_hint, now()),
                )
                token_id = cursor.lastrowid
            self.send_json(201, {"id": token_id, "name": name, "token": raw_token, "hint": token_hint, "active": True})
            return

        if path == "/api/billing/call":
            api_user = self.require_api_token()
            user = (api_user[1], api_user[2], api_user[3], api_user[4]) if api_user else None
            if not user:
                return
            token_id = api_user[0]
            model_name = str(payload.get("model", "")).strip()
            key = str(payload.get("idempotencyKey") or self.headers.get("Idempotency-Key") or "").strip()
            usage = payload.get("usage") or {}
            input_tokens = max(0, int(usage.get("inputTokens", 0) or 0))
            output_tokens = max(0, int(usage.get("outputTokens", 0) or 0))
            if not model_name or not key or len(key) > 128:
                self.send_json(400, {"error": "model_and_idempotency_key_required"})
                return
            with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                    existing = db.execute("SELECT amount_micros, status FROM ledger WHERE user_id=? AND idempotency_key=?", (user[0], key)).fetchone()
                    if existing:
                        balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user[0],)).fetchone()[0]
                        db.execute("COMMIT")
                        self.send_json(200, {"charged": micros_to_dollars(existing[0]), "balance": micros_to_dollars(balance), "idempotent": True, "status": existing[1]})
                        return
                    model = db.execute("SELECT billing_unit, price_micros, active FROM models WHERE name=?", (model_name,)).fetchone()
                    if not model or not model[2]:
                        raise ValueError("model_not_available")
                    unit, price_micros, _ = model
                    if unit == "per_token":
                        quantity = input_tokens + output_tokens
                        if quantity <= 0:
                            raise ValueError("token_usage_required")
                        amount = (price_micros * quantity + 999) // 1000
                    else:
                        amount = price_micros
                    balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user[0],)).fetchone()[0]
                    if balance < amount:
                        raise ValueError("insufficient_balance")
                    db.execute("UPDATE users SET balance_micros=balance_micros-? WHERE id=?", (amount, user[0]))
                    db.execute("INSERT INTO ledger(user_id, model_name, idempotency_key, amount_micros, billing_unit, input_tokens, output_tokens, status, created_at, token_id) VALUES (?, ?, ?, ?, ?, ?, ?, 'charged', ?, ?)", (user[0], model_name, key, amount, unit, input_tokens, output_tokens, now(), token_id))
                    new_balance = balance - amount
                    db.execute("COMMIT")
                except ValueError as exc:
                    db.execute("ROLLBACK")
                    self.send_json(400, {"error": str(exc)})
                    return
                except sqlite3.IntegrityError:
                    db.execute("ROLLBACK")
                    self.send_json(409, {"error": "duplicate_idempotency_key"})
                    return
            self.send_json(200, {"charged": micros_to_dollars(amount), "balance": micros_to_dollars(new_balance), "idempotent": False, "status": "charged"})
            return
        self.send_json(404, {"error": "not_found"})

    def do_PUT(self):
        path = urlparse(self.path).path
        prefix = "/api/admin/models/"
        if not path.startswith(prefix):
            self.send_json(404, {"error": "not_found"})
            return
        admin = self.require_user(admin=True)
        if not admin:
            return
        name = path[len(prefix):]
        try:
            payload = self.read_json()
            price_micros = dollars_to_micros(payload.get("price"))
            billing_unit = payload.get("billingUnit")
            if billing_unit not in ("per_task", "per_token"):
                raise ValueError("billingUnit must be per_task or per_token")
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE models SET price_micros=?, billing_unit=?, updated_at=? WHERE name=?", (price_micros, billing_unit, now(), name))
            if cursor.rowcount != 1:
                self.send_json(404, {"error": "model_not_found"})
                return
        self.send_json(200, {"model": name, "price": micros_to_dollars(price_micros), "billingUnit": billing_unit})

    def do_DELETE(self):
        path = urlparse(self.path).path
        prefix = "/api/tokens/"
        if not path.startswith(prefix):
            self.send_json(404, {"error": "not_found"})
            return
        user = self.require_user()
        if not user:
            return
        try:
            token_id = int(path[len(prefix):])
        except ValueError:
            self.send_json(400, {"error": "invalid_token_id"})
            return
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE api_tokens SET active=0 WHERE id=? AND user_id=?", (token_id, user[0]))
        if cursor.rowcount != 1:
            self.send_json(404, {"error": "token_not_found"})
            return
        self.send_json(200, {"id": token_id, "active": False})


def main():
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("NBAPI running at http://127.0.0.1:8765")
    print("Demo admin: admin / admin123")
    print("Demo user: demo / demo123")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
