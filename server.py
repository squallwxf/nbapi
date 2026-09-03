import hashlib
import ipaddress
import json
import os
import secrets
import sqlite3
import threading
import time
import traceback
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("NBAPI_DB_PATH", str(ROOT / "nbapi.sqlite3"))).expanduser()
HTML_PATH = ROOT / "api-website.html"
UPSTREAM = "https://ai.krapi.cn"
MICROS_PER_DOLLAR = 1_000_000
TOKEN_PREFIX = "nb_sk_"
DEFAULT_SUPER_ADMIN_USERNAME = "squallwxf"
DEFAULT_SUPER_ADMIN_PASSWORD = os.environ.get("NBAPI_SUPER_ADMIN_PASSWORD", "")
DEFAULT_SUPER_ADMIN_EMAIL = "squallwxf@nbapi.local"
PROXY_PREFIXES = ("/v1/", "/v1beta/")
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "NBAPI_ALLOWED_ORIGINS",
        "https://nbapi.win,http://127.0.0.1:8000,http://localhost:8000",
    ).split(",")
    if origin.strip()
}
MAX_REQUEST_BODY = 2_000_000
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10
_rate_limit_lock = threading.Lock()
_rate_limit_buckets: dict[tuple[str, str], list[float]] = {}
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}

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
CHANNEL_ROWS = [
    ("默认主渠道", "https://ai.krapi.cn", "", 1, 100, "主站默认模型渠道"),
    ("备用渠道", "https://ai.krapi.cn", "", 1, 200, "备用或灰度渠道"),
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
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(
            """
            PRAGMA journal_mode = WAL;
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              email TEXT NOT NULL DEFAULT '',
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL CHECK(role IN ('user', 'admin', 'super_admin')),
              active INTEGER NOT NULL DEFAULT 1,
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
              token_secret TEXT NOT NULL DEFAULT '',
              token_hint TEXT NOT NULL,
              active INTEGER NOT NULL DEFAULT 1,
              created_at INTEGER NOT NULL,
              last_used_at INTEGER,
              expires_at INTEGER,
              token_group TEXT NOT NULL DEFAULT 'default',
              quota_micros INTEGER NOT NULL DEFAULT 0,
              quota_unlimited INTEGER NOT NULL DEFAULT 1,
              used_micros INTEGER NOT NULL DEFAULT 0,
              allowed_models TEXT NOT NULL DEFAULT '',
              ip_allowlist TEXT NOT NULL DEFAULT ''
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
              client_ip TEXT NOT NULL DEFAULT '',
              latency_ms INTEGER NOT NULL DEFAULT 0,
              request_path TEXT NOT NULL DEFAULT '',
              request_id TEXT NOT NULL DEFAULT '',
              UNIQUE(user_id, idempotency_key)
            );
            CREATE TABLE IF NOT EXISTS settings (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS channels (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL UNIQUE,
              upstream_base_url TEXT NOT NULL,
              upstream_api_key TEXT NOT NULL DEFAULT '',
              active INTEGER NOT NULL DEFAULT 1,
              priority INTEGER NOT NULL DEFAULT 100,
              note TEXT NOT NULL DEFAULT '',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            """
        )
        user_sql = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if user_sql and "super_admin" not in (user_sql[0] or ""):
            db.execute("ALTER TABLE users RENAME TO users_legacy")
            db.execute(
                """
                CREATE TABLE users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  email TEXT NOT NULL DEFAULT '',
                  password_hash TEXT NOT NULL,
                  role TEXT NOT NULL CHECK(role IN ('user', 'admin', 'super_admin')),
                  active INTEGER NOT NULL DEFAULT 1,
                  balance_micros INTEGER NOT NULL DEFAULT 0,
                  created_at INTEGER NOT NULL
                )
                """
            )
            legacy_columns = {row[1] for row in db.execute("PRAGMA table_info(users_legacy)")}
            email_expr = "email" if "email" in legacy_columns else "''"
            db.execute(
                f"INSERT INTO users(id, username, email, password_hash, role, active, balance_micros, created_at) SELECT id, username, {email_expr}, password_hash, role, 1, balance_micros, created_at FROM users_legacy"
            )
            db.execute("DROP TABLE users_legacy")
        user_columns = {row[1] for row in db.execute("PRAGMA table_info(users)")}
        if "email" not in user_columns:
            db.execute("ALTER TABLE users ADD COLUMN email TEXT NOT NULL DEFAULT ''")
        if "active" not in user_columns:
            db.execute("ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
        columns = {row[1] for row in db.execute("PRAGMA table_info(ledger)")}
        if "token_id" not in columns:
            db.execute("ALTER TABLE ledger ADD COLUMN token_id INTEGER REFERENCES api_tokens(id)")
        for column, definition in (
            ("client_ip", "TEXT NOT NULL DEFAULT ''"),
            ("latency_ms", "INTEGER NOT NULL DEFAULT 0"),
            ("request_path", "TEXT NOT NULL DEFAULT ''"),
            ("request_id", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in columns:
                db.execute(f"ALTER TABLE ledger ADD COLUMN {column} {definition}")
        token_columns = {row[1] for row in db.execute("PRAGMA table_info(api_tokens)")}
        if "token_secret" not in token_columns:
            db.execute("ALTER TABLE api_tokens ADD COLUMN token_secret TEXT NOT NULL DEFAULT ''")
        for column, definition in (
            ("token_group", "TEXT NOT NULL DEFAULT 'default'"),
            ("quota_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("quota_unlimited", "INTEGER NOT NULL DEFAULT 1"),
            ("used_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("allowed_models", "TEXT NOT NULL DEFAULT ''"),
            ("ip_allowlist", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in token_columns:
                db.execute(f"ALTER TABLE api_tokens ADD COLUMN {column} {definition}")
        # Keep token hashes usable while removing legacy plaintext copies at rest.
        db.execute("UPDATE api_tokens SET token_secret='' WHERE token_secret<>''")
        timestamp = now()
        super_admin_row = db.execute(
            "SELECT id, username FROM users WHERE role='super_admin' ORDER BY id LIMIT 1"
        ).fetchone()
        desired_super_admin = db.execute(
            "SELECT id FROM users WHERE lower(username)=lower(?) LIMIT 1",
            (DEFAULT_SUPER_ADMIN_USERNAME,),
        ).fetchone()
        if desired_super_admin:
            db.execute("UPDATE users SET role='super_admin', active=1 WHERE id=?", (desired_super_admin[0],))
            if super_admin_row and super_admin_row[0] != desired_super_admin[0]:
                db.execute("UPDATE users SET role='admin' WHERE id=?", (super_admin_row[0],))
        elif super_admin_row:
            db.execute("UPDATE users SET username=?, email=?, role='super_admin', active=1 WHERE id=?", (DEFAULT_SUPER_ADMIN_USERNAME, DEFAULT_SUPER_ADMIN_EMAIL, super_admin_row[0]))
        else:
            if not DEFAULT_SUPER_ADMIN_PASSWORD:
                raise RuntimeError("NBAPI_SUPER_ADMIN_PASSWORD is required when initializing a new database")
            db.execute(
                "INSERT OR IGNORE INTO users(username, email, password_hash, role, active, balance_micros, created_at) VALUES (?, ?, ?, 'super_admin', 1, ?, ?)",
                (DEFAULT_SUPER_ADMIN_USERNAME, DEFAULT_SUPER_ADMIN_EMAIL, hash_password(DEFAULT_SUPER_ADMIN_PASSWORD), 100 * MICROS_PER_DOLLAR, timestamp),
            )
        for name, provider_label, provider, kind, billing_unit, price_micros in MODEL_ROWS:
            db.execute(
                """INSERT OR IGNORE INTO models
                (name, provider_label, provider, kind, billing_unit, price_micros, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, provider_label, provider, kind, billing_unit, price_micros, timestamp),
            )
        for name, upstream_base_url, upstream_api_key, active, priority, note in CHANNEL_ROWS:
            db.execute(
                """INSERT OR IGNORE INTO channels
                (name, upstream_base_url, upstream_api_key, active, priority, note, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, upstream_base_url, upstream_api_key, active, priority, note, timestamp, timestamp),
            )
        db.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES ('upstream_api_key', '', ?)",
            (timestamp,),
        )


def json_bytes(payload) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def should_proxy_path(path: str) -> bool:
    return path == "/v1" or path == "/v1beta" or path.startswith(PROXY_PREFIXES)


def try_parse_json_bytes(body: bytes):
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def extract_model_name(path: str, payload) -> str:
    if path.startswith("/v1beta/models/"):
        model_part = path[len("/v1beta/models/"):]
        suffix = ":generateContent"
        if model_part.endswith(suffix):
            return unquote(model_part[:-len(suffix)]).strip()
    if isinstance(payload, dict):
        model = str(payload.get("model", "")).strip()
        if model:
            return model
    return ""


def extract_usage_counts(payload) -> tuple[int, int]:
    if not isinstance(payload, dict):
        return 0, 0
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        usage = payload.get("usageMetadata") if isinstance(payload.get("usageMetadata"), dict) else {}
    if not isinstance(usage, dict):
        return 0, 0
    candidates = (
        ("inputTokens", "input_tokens", "prompt_tokens", "promptTokens"),
        ("outputTokens", "output_tokens", "completion_tokens", "completionTokens"),
        ("totalTokens", "total_tokens", "totalTokens"),
    )

    def pick(keys):
        for key in keys:
            value = usage.get(key)
            if value is not None:
                try:
                    return max(0, int(value))
                except (TypeError, ValueError):
                    continue
        return None

    input_tokens = pick(candidates[0])
    output_tokens = pick(candidates[1])
    total_tokens = pick(candidates[2])
    if input_tokens is None and output_tokens is None and total_tokens is not None:
        return total_tokens, 0
    return input_tokens or 0, output_tokens or 0


def get_upstream_route(db):
    row = db.execute(
        "SELECT id, name, upstream_base_url, upstream_api_key FROM channels WHERE active=1 ORDER BY priority ASC, id ASC LIMIT 1"
    ).fetchone()
    if row:
        base_url = str(row[2] or "").strip() or UPSTREAM
        if base_url.lower().endswith("/v1") or base_url.lower().endswith("/v1beta"):
            base_url = base_url.rsplit("/", 1)[0]
        api_key = str(row[3] or "").strip() or get_setting(db, "upstream_api_key", "")
        return {
            "channel_id": row[0],
            "channel_name": row[1],
            "base_url": base_url.rstrip("/"),
            "api_key": api_key,
        }
    return {
        "channel_id": None,
        "channel_name": None,
        "base_url": UPSTREAM.rstrip("/"),
        "api_key": get_setting(db, "upstream_api_key", ""),
    }


def fetch_model_row(db, model_name: str):
    return db.execute(
        "SELECT name, provider_label, provider, kind, billing_unit, price_micros, active FROM models WHERE name=?",
        (model_name,),
    ).fetchone()


def split_lines(value: str) -> list[str]:
    return [line.strip() for line in str(value or "").replace(",", "\n").splitlines() if line.strip()]


def token_allows_model(allowed_models: str, model_name: str) -> bool:
    models = split_lines(allowed_models)
    return not models or model_name in models


def token_allows_ip(ip_allowlist: str, client_ip: str) -> bool:
    entries = split_lines(ip_allowlist)
    if not entries:
        return True
    try:
        address = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    for entry in entries:
        try:
            if address in ipaddress.ip_network(entry, strict=False):
                return True
        except ValueError:
            if entry == client_ip:
                return True
    return False


def bill_ledger(db, user_id: int, token_id: int, model_name: str, idempotency_key: str, amount_micros: int, billing_unit: str, input_tokens: int = 0, output_tokens: int = 0, client_ip: str = "", latency_ms: int = 0, request_path: str = "", request_id: str = ""):
    existing = db.execute(
        "SELECT amount_micros, status FROM ledger WHERE user_id=? AND idempotency_key=?",
        (user_id, idempotency_key),
    ).fetchone()
    if existing:
        balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user_id,)).fetchone()[0]
        return {
            "idempotent": True,
            "amount_micros": existing[0],
            "balance_micros": balance,
            "status": existing[1],
        }
    balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user_id,)).fetchone()[0]
    if balance < amount_micros:
        raise ValueError("insufficient_balance")
    token_row = db.execute("SELECT quota_micros, quota_unlimited, used_micros FROM api_tokens WHERE id=? AND user_id=? AND active=1", (token_id, user_id)).fetchone()
    if not token_row:
        raise ValueError("invalid_or_inactive_api_key")
    if not token_row[1] and token_row[2] + amount_micros > token_row[0]:
        raise ValueError("token_quota_exceeded")
    db.execute("UPDATE users SET balance_micros=balance_micros-? WHERE id=?", (amount_micros, user_id))
    db.execute("UPDATE api_tokens SET used_micros=used_micros+? WHERE id=?", (amount_micros, token_id))
    db.execute(
        """INSERT INTO ledger(user_id, model_name, idempotency_key, amount_micros, billing_unit,
                              input_tokens, output_tokens, status, created_at, token_id,
                              client_ip, latency_ms, request_path, request_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'charged', ?, ?, ?, ?, ?, ?)""",
        (user_id, model_name, idempotency_key, amount_micros, billing_unit, input_tokens, output_tokens, now(), token_id, client_ip, latency_ms, request_path, request_id),
    )
    return {
        "idempotent": False,
        "amount_micros": amount_micros,
        "balance_micros": balance - amount_micros,
        "status": "charged",
    }


def mask_secret(value: str, prefix: int = 4, suffix: int = 4) -> str:
    value = value or ""
    if not value:
        return ""
    if len(value) <= prefix + suffix:
        return "*" * len(value)
    return f"{value[:prefix]}{'*' * 8}{value[-suffix:]}"


def get_setting(db, key: str, default: str = "") -> str:
    row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(db, key: str, value: str) -> None:
    db.execute(
        """INSERT INTO settings(key, value, updated_at)
           VALUES (?, ?, ?)
           ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
        (key, value, now()),
    )


def serialize_user(row):
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "role": row[3],
        "active": bool(row[4]),
        "balance": micros_to_dollars(row[5]),
        "createdAt": row[6],
    }


def serialize_channel(row):
    return {
        "id": row[0],
        "name": row[1],
        "upstreamBaseUrl": row[2],
        "upstreamApiKeySet": bool(row[3]),
        "upstreamApiKeyHint": mask_secret(row[3]),
        "active": bool(row[4]),
        "priority": row[5],
        "note": row[6],
        "createdAt": row[7],
        "updatedAt": row[8],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "NBAPI/1.0"

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def send_json(self, status: int, payload) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self) -> None:
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Authorization, X-NBAPI-Key, Content-Type, Idempotency-Key")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")

    def _client_ip(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        return forwarded or self.client_address[0]

    def _rate_limited(self, bucket: str) -> bool:
        now_value = time.monotonic()
        key = (self._client_ip(), bucket)
        with _rate_limit_lock:
            recent = [stamp for stamp in _rate_limit_buckets.get(key, []) if now_value - stamp < RATE_LIMIT_WINDOW]
            limited = len(recent) >= RATE_LIMIT_MAX
            if not limited:
                recent.append(now_value)
            _rate_limit_buckets[key] = recent
            if len(_rate_limit_buckets) > 5000:
                for old_key, stamps in list(_rate_limit_buckets.items()):
                    if not stamps or now_value - stamps[-1] >= RATE_LIMIT_WINDOW:
                        _rate_limit_buckets.pop(old_key, None)
            return limited

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_REQUEST_BODY:
            raise ValueError("request body too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def _send_raw_response(self, status: int, headers: dict, body: bytes) -> None:
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() in HOP_BY_HOP_HEADERS or key.lower() == "content-length":
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _estimate_token_quantity(self, payload) -> int:
        if not isinstance(payload, dict):
            return 1
        for key in ("max_tokens", "maxTokens", "max_completion_tokens", "maxCompletionTokens"):
            value = payload.get(key)
            if value is not None:
                try:
                    return max(1, int(value))
                except (TypeError, ValueError):
                    continue
        text = json.dumps(payload, ensure_ascii=False)
        return max(1, min(100000, len(text) // 4))

    def _proxy_upstream(self, method: str) -> bool:
        parsed = urlparse(self.path)
        path = parsed.path
        if not should_proxy_path(path):
            return False

        api_user = self.require_api_token()
        if not api_user:
            return True

        started_at = time.perf_counter()
        client_ip = self.headers.get("X-Forwarded-For", "").split(",")[0].strip() or self.client_address[0]
        body = b""
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
        payload = try_parse_json_bytes(body)
        model_name = extract_model_name(path, payload)

        if method in ("POST", "PUT", "PATCH", "DELETE") and not model_name:
            self.send_json(400, {"error": "model_required"})
            return True

        with sqlite3.connect(DB_PATH) as db:
            route = get_upstream_route(db)
            if not route["api_key"]:
                self.send_json(503, {"error": "upstream_api_key_not_configured"})
                return True

            model_row = None
            if model_name:
                model_row = fetch_model_row(db, model_name)
                if not model_row or not model_row[6]:
                    self.send_json(400, {"error": "model_not_available"})
                    return True
                if not token_allows_model(api_user[9], model_name):
                    self.send_json(403, {"error": "model_not_allowed_for_token"})
                    return True
                if model_row[4] == "per_task":
                    balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (api_user[1],)).fetchone()[0]
                    if balance < model_row[5]:
                        self.send_json(400, {"error": "insufficient_balance"})
                        return True

            upstream_url = f"{route['base_url']}{path}"
            if parsed.query:
                upstream_url = f"{upstream_url}?{parsed.query}"
            upstream_headers = {}
            for key, value in self.headers.items():
                lower_key = key.lower()
                if lower_key in HOP_BY_HOP_HEADERS or lower_key in {"host", "content-length", "authorization"}:
                    continue
                upstream_headers[key] = value
            upstream_headers["Authorization"] = f"Bearer {route['api_key']}"
            if body and "content-type" not in {key.lower() for key in upstream_headers}:
                upstream_headers["Content-Type"] = self.headers.get("Content-Type", "application/json")
            request = Request(
                upstream_url,
                data=body if method in ("POST", "PUT", "PATCH", "DELETE") else None,
                headers=upstream_headers,
                method=method,
            )
            try:
                with urlopen(request, timeout=300) as response:
                    resp_status = response.status
                    resp_headers = dict(response.headers.items())
                    resp_body = response.read()
            except HTTPError as exc:
                resp_status = exc.code
                resp_headers = dict(exc.headers.items()) if exc.headers else {}
                resp_body = exc.read() or b""
            except URLError as exc:
                self.send_json(502, {"error": "upstream_unreachable", "detail": str(getattr(exc, "reason", exc))})
                return True

        if not (200 <= resp_status < 300):
            self._send_raw_response(resp_status, resp_headers, resp_body)
            return True

        if model_row:
            response_payload = try_parse_json_bytes(resp_body)
            billing_unit = model_row[4]
            price_micros = model_row[5]
            input_tokens = 0
            output_tokens = 0
            if billing_unit == "per_token":
                input_tokens, output_tokens = extract_usage_counts(response_payload)
                quantity = input_tokens + output_tokens
                if quantity <= 0:
                    quantity = self._estimate_token_quantity(payload)
                amount_micros = (price_micros * quantity + 999) // 1000
            else:
                amount_micros = price_micros

            idempotency_key = (
                str(self.headers.get("Idempotency-Key", "")).strip()
                or str(response_payload.get("id") if isinstance(response_payload, dict) else "").strip()
                or str(response_payload.get("task_id") if isinstance(response_payload, dict) else "").strip()
                or hashlib.sha256((method + "|" + path + "|" + body.decode("utf-8", "ignore")).encode("utf-8")).hexdigest()
            )
            with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                    charge_result = bill_ledger(
                        db,
                        api_user[1],
                        api_user[0],
                        model_name,
                        idempotency_key,
                        amount_micros,
                        billing_unit,
                        input_tokens,
                        output_tokens,
                        client_ip,
                        round((time.perf_counter() - started_at) * 1000),
                        path,
                        idempotency_key,
                    )
                    db.execute("COMMIT")
                except ValueError as exc:
                    db.execute("ROLLBACK")
                    self.send_json(402 if str(exc) in ("insufficient_balance", "token_quota_exceeded") else 400, {"error": str(exc)})
                    return True
                except sqlite3.IntegrityError:
                    db.execute("ROLLBACK")
                    self.send_json(409, {"error": "duplicate_idempotency_key"})
                    return True
            if charge_result["idempotent"]:
                resp_headers["X-NBAPI-Idempotent"] = "1"
            resp_headers["X-NBAPI-Charged"] = micros_to_dollars(charge_result["amount_micros"])
            resp_headers["X-NBAPI-Balance"] = micros_to_dollars(charge_result["balance_micros"])

        self._send_raw_response(resp_status, resp_headers, resp_body)
        return True

    def current_user(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:].strip()
        with sqlite3.connect(DB_PATH) as db:
            return db.execute(
                """SELECT u.id, u.username, u.role, u.balance_micros
                   FROM sessions s JOIN users u ON u.id=s.user_id
                   WHERE s.token=? AND s.expires_at>? AND u.active=1""",
                (token, now()),
            ).fetchone()

    def require_user(self, admin=False):
        user = self.current_user()
        if not user:
            self.send_json(401, {"error": "authentication_required"})
            return None
        if admin and user[2] not in ("admin", "super_admin"):
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
                """SELECT t.id, t.user_id, u.username, u.role, u.balance_micros,
                          t.token_group, t.quota_micros, t.quota_unlimited, t.used_micros,
                          t.allowed_models, t.ip_allowlist
                   FROM api_tokens t JOIN users u ON u.id=t.user_id
                   WHERE t.token_hash=? AND t.active=1
                     AND u.active=1
                     AND (t.expires_at IS NULL OR t.expires_at>?)""",
                (token_hash, now()),
            ).fetchone()
            if row:
                db.execute("UPDATE api_tokens SET last_used_at=? WHERE id=?", (now(), row[0]))
        if not row:
            self.send_json(401, {"error": "invalid_or_inactive_api_key"})
            return None
        client_ip = self.headers.get("X-Forwarded-For", "").split(",")[0].strip() or self.client_address[0]
        if not token_allows_ip(row[10], client_ip):
            self.send_json(403, {"error": "ip_not_allowed"})
            return None
        return row

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            try:
                with sqlite3.connect(DB_PATH, timeout=2) as db:
                    db.execute("SELECT 1").fetchone()
                self.send_json(200, {"status": "ok", "service": "nbapi", "timestamp": now()})
            except sqlite3.Error:
                self.send_json(503, {"status": "error", "service": "nbapi"})
            return
        if self._proxy_upstream("GET"):
            return
        if path == "/api/admin/config":
            admin = self.require_user(admin=True)
            if not admin:
                return
            with sqlite3.connect(DB_PATH) as db:
                route = get_upstream_route(db)
            self.send_json(200, {
                "upstreamBaseUrl": route["base_url"],
                "activeChannelName": route["channel_name"],
                "upstreamApiKeySet": bool(route["api_key"]),
                "upstreamApiKeyHint": mask_secret(route["api_key"]),
            })
            return
        if path == "/api/admin/users":
            admin = self.require_user(admin=True)
            if not admin:
                return
            query = parse_qs(urlparse(self.path).query)
            search = str(query.get("q", [""])[0]).strip().lower()
            try:
                page = max(1, int(query.get("page", ["1"])[0] or 1))
            except ValueError:
                page = 1
            try:
                page_size = min(50, max(1, int(query.get("pageSize", ["10"])[0] or 10)))
            except ValueError:
                page_size = 10
            offset = (page - 1) * page_size
            with sqlite3.connect(DB_PATH) as db:
                params = []
                where = ""
                if search:
                    where = "WHERE lower(username) LIKE ? OR lower(email) LIKE ? OR lower(role) LIKE ?"
                    like = f"%{search}%"
                    params = [like, like, like]
                total = db.execute(f"SELECT COUNT(*) FROM users {where}", params).fetchone()[0]
                rows = db.execute(
                    f"SELECT id, username, email, role, active, balance_micros, created_at FROM users {where} ORDER BY id DESC LIMIT ? OFFSET ?",
                    [*params, page_size, offset],
                ).fetchall()
            self.send_json(200, {
                "items": [serialize_user(row) for row in rows],
                "page": page,
                "pageSize": page_size,
                "total": total,
                "totalPages": max(1, (total + page_size - 1) // page_size),
            })
            return
        if path == "/api/admin/channels":
            admin = self.require_user(admin=True)
            if not admin:
                return
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute(
                    "SELECT id, name, upstream_base_url, upstream_api_key, active, priority, note, created_at, updated_at FROM channels ORDER BY priority ASC, id ASC"
                ).fetchall()
            self.send_json(200, {"items": [serialize_channel(row) for row in rows]})
            return
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
                with sqlite3.connect(DB_PATH) as db:
                    row = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (user[0],)).fetchone()
                self.send_json(200, {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "role": row[3],
                    "active": bool(row[4]),
                    "balance": micros_to_dollars(row[5]),
                    "createdAt": row[6],
                })
            return
        if path == "/api/ledger":
            user = self.require_user()
            if user:
                query = parse_qs(urlparse(self.path).query)
                get_filter = lambda key: str(query.get(key, [""])[0]).strip()
                def as_int(key, default, minimum, maximum):
                    try:
                        return min(maximum, max(minimum, int(get_filter(key) or default)))
                    except ValueError:
                        return default
                page = as_int("page", 1, 1, 1000000)
                page_size = as_int("pageSize", 10, 1, 100)
                filters = ["l.user_id=?"]
                params = [user[0]]
                for key, expression in (("model", "lower(l.model_name) LIKE ?"), ("requestId", "lower(COALESCE(l.request_id, l.idempotency_key)) LIKE ?"), ("token", "(lower(COALESCE(t.name, '')) LIKE ? OR lower(COALESCE(t.token_hint, '')) LIKE ?)") , ("group", "lower(COALESCE(t.token_group, '')) LIKE ?")):
                    value = get_filter(key).lower()
                    if value:
                        filters.append(expression)
                        params.extend([f"%{value}%"] * (2 if key == "token" else 1))
                if get_filter("status"):
                    filters.append("l.status=?")
                    params.append(get_filter("status"))
                if get_filter("type"):
                    filters.append("l.billing_unit=?")
                    params.append(get_filter("type"))
                def parse_time(value, end=False):
                    if not value:
                        return None
                    try:
                        return int(time.mktime(time.strptime(value[:16], "%Y-%m-%dT%H:%M"))) + (59 if end else 0)
                    except ValueError:
                        return None
                start_time = parse_time(get_filter("from"))
                end_time = parse_time(get_filter("to"), True)
                if start_time is not None:
                    filters.append("l.created_at>=?"); params.append(start_time)
                if end_time is not None:
                    filters.append("l.created_at<=?"); params.append(end_time)
                where = " AND ".join(filters)
                with sqlite3.connect(DB_PATH) as db:
                    total, amount_total, input_total, output_total = db.execute(
                        f"SELECT COUNT(*), COALESCE(SUM(l.amount_micros),0), COALESCE(SUM(l.input_tokens),0), COALESCE(SUM(l.output_tokens),0) FROM ledger l LEFT JOIN api_tokens t ON t.id=l.token_id WHERE {where}", params
                    ).fetchone()
                    rows = db.execute(
                        f"SELECT l.id, l.model_name, l.amount_micros, l.billing_unit, l.input_tokens, l.output_tokens, l.status, l.created_at, l.token_id, COALESCE(t.name,''), COALESCE(t.token_hint,''), COALESCE(t.token_group,'default'), COALESCE(l.request_id,l.idempotency_key), COALESCE(l.client_ip,''), COALESCE(l.latency_ms,0), COALESCE(l.request_path,'') FROM ledger l LEFT JOIN api_tokens t ON t.id=l.token_id WHERE {where} ORDER BY l.id DESC LIMIT ? OFFSET ?",
                        [*params, page_size, (page - 1) * page_size],
                    ).fetchall()
                self.send_json(200, {"items": [{
                    "id": r[0], "model": r[1], "amount": micros_to_dollars(r[2]), "billingUnit": r[3], "inputTokens": r[4], "outputTokens": r[5], "status": r[6], "createdAt": r[7], "tokenId": r[8], "tokenName": r[9] or "未关联令牌", "tokenHint": r[10], "tokenGroup": r[11], "requestId": r[12], "ip": r[13] or "-", "latencyMs": r[14], "path": r[15]
                } for r in rows], "stats": {"amount": micros_to_dollars(amount_total), "requests": total, "inputTokens": input_total, "outputTokens": output_total, "tokens": input_total + output_total}, "page": page, "pageSize": page_size, "total": total, "totalPages": max(1, (total + page_size - 1) // page_size)})
            return
        if path == "/api/tokens":
            user = self.require_user()
            if user:
                with sqlite3.connect(DB_PATH) as db:
                    rows = db.execute(
                        "SELECT id, name, token_hint, active, created_at, last_used_at, expires_at, token_group, quota_micros, quota_unlimited, used_micros, allowed_models, ip_allowlist FROM api_tokens WHERE user_id=? ORDER BY id DESC",
                        (user[0],),
                    ).fetchall()
                self.send_json(200, {"items": [{
                    "id": r[0], "name": r[1], "hint": r[2], "token": None, "canCopyFullToken": False, "active": bool(r[3]),
                    "createdAt": r[4], "lastUsedAt": r[5], "expiresAt": r[6], "group": r[7],
                    "quota": micros_to_dollars(r[8]), "unlimitedQuota": bool(r[9]), "usedQuota": micros_to_dollars(r[10]),
                    "allowedModels": split_lines(r[11]), "ipAllowlist": split_lines(r[12])
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
        if self._proxy_upstream("POST"):
            return
        try:
            path = urlparse(self.path).path
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
                return

            if path == "/api/auth/login":
                if self._rate_limited("login"):
                    self.send_json(429, {"error": "rate_limited"})
                    return
                username = str(payload.get("username", "")).strip()
                password = str(payload.get("password", ""))
                with sqlite3.connect(DB_PATH) as db:
                    row = db.execute(
                        "SELECT id, username, email, password_hash, role, active, balance_micros, created_at FROM users WHERE username=? OR email=?",
                        (username, username),
                    ).fetchone()
                    if not row or not verify_password(password, row[3]):
                        self.send_json(401, {"error": "invalid_credentials"})
                        return
                    if not row[5]:
                        self.send_json(403, {"error": "user_disabled"})
                        return
                    token = secrets.token_urlsafe(32)
                    db.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)", (token, row[0], now() + 7 * 86400))
                self.send_json(200, {
                    "token": token,
                    "user": {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "role": row[4],
                        "active": bool(row[5]),
                        "balance": micros_to_dollars(row[6]),
                        "createdAt": row[7],
                    },
                })
                return

            if path == "/api/auth/password":
                user = self.require_user()
                if not user:
                    return
                current_password = str(payload.get("currentPassword", ""))
                new_password = str(payload.get("newPassword", ""))
                if len(new_password) < 12:
                    self.send_json(400, {"error": "password_too_short"})
                    return
                with sqlite3.connect(DB_PATH) as db:
                    row = db.execute("SELECT password_hash FROM users WHERE id=?", (user[0],)).fetchone()
                    if not row or not verify_password(current_password, row[0]):
                        self.send_json(401, {"error": "current_password_invalid"})
                        return
                    db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), user[0]))
                    db.execute("DELETE FROM sessions WHERE user_id=? AND token<>?", (user[0], self.headers.get("Authorization", "")[7:].strip()))
                self.send_json(200, {"updated": True})
                return

            if path == "/api/auth/register":
                if self._rate_limited("register"):
                    self.send_json(429, {"error": "rate_limited"})
                    return
                username = str(payload.get("username", "")).strip()
                email = str(payload.get("email", "")).strip().lower()
                password = str(payload.get("password", ""))
                if not (3 <= len(username) <= 32):
                    self.send_json(400, {"error": "username_length_invalid"})
                    return
                if not username.replace("_", "").replace("-", "").isalnum():
                    self.send_json(400, {"error": "username_format_invalid"})
                    return
                if "@" not in email or "." not in email or len(email) > 120:
                    self.send_json(400, {"error": "email_invalid"})
                    return
                if len(password) < 6:
                    self.send_json(400, {"error": "password_too_short"})
                    return
                timestamp = now()
                try:
                    with sqlite3.connect(DB_PATH) as db:
                        existing_email = db.execute("SELECT id FROM users WHERE lower(email)=lower(?) AND email<>''", (email,)).fetchone()
                        if existing_email:
                            self.send_json(409, {"error": "email_already_exists"})
                            return
                        cursor = db.execute(
                            "INSERT INTO users(username, email, password_hash, role, active, balance_micros, created_at) VALUES (?, ?, ?, 'user', 1, ?, ?)",
                            (username, email, hash_password(password), 0, timestamp),
                        )
                        user_id = cursor.lastrowid
                        token = secrets.token_urlsafe(32)
                        db.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, now() + 7 * 86400))
                        row = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (user_id,)).fetchone()
                except sqlite3.IntegrityError:
                    self.send_json(409, {"error": "username_already_exists"})
                    return
                self.send_json(201, {
                    "token": token,
                    "user": {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "role": row[3],
                        "active": bool(row[4]),
                        "balance": micros_to_dollars(row[5]),
                        "createdAt": row[6],
                    },
                })
                return

            if path == "/api/tokens/bulk":
                user = self.require_user()
                if not user:
                    return
                ids = payload.get("ids")
                action = str(payload.get("action", "")).strip().lower()
                if action not in ("enable", "disable", "delete") or not isinstance(ids, list) or not ids or len(ids) > 100:
                    self.send_json(400, {"error": "invalid_bulk_token_action"})
                    return
                try:
                    token_ids = sorted({int(value) for value in ids})
                except (TypeError, ValueError):
                    self.send_json(400, {"error": "invalid_token_id"})
                    return
                placeholders = ",".join("?" for _ in token_ids)
                with sqlite3.connect(DB_PATH) as db:
                    if action == "delete":
                        db.execute(f"UPDATE ledger SET token_id=NULL WHERE user_id=? AND token_id IN ({placeholders})", [user[0], *token_ids])
                        cursor = db.execute(f"DELETE FROM api_tokens WHERE user_id=? AND id IN ({placeholders})", [user[0], *token_ids])
                        self.send_json(200, {"deleted": cursor.rowcount})
                        return
                    cursor = db.execute(
                        f"UPDATE api_tokens SET active=? WHERE user_id=? AND id IN ({placeholders})",
                        [1 if action == "enable" else 0, user[0], *token_ids],
                    )
                self.send_json(200, {"updated": cursor.rowcount, "active": action == "enable"})
                return

            if path == "/api/tokens":
                user = self.require_user()
                if not user:
                    return
                name = str(payload.get("name", "")).strip() or "未命名令牌"
                if len(name) > 64 or any(ord(char) < 32 for char in name):
                    self.send_json(400, {"error": "token_name_too_long"})
                    return
                group_name = str(payload.get("group", "default")).strip() or "default"
                if len(group_name) > 64:
                    self.send_json(400, {"error": "token_group_too_long"})
                    return
                try:
                    count = max(1, min(50, int(payload.get("count", 1))))
                except (TypeError, ValueError):
                    self.send_json(400, {"error": "invalid_token_count"})
                    return
                unlimited = bool(payload.get("unlimitedQuota", True))
                try:
                    quota_micros = dollars_to_micros(payload.get("quota", 0)) if not unlimited else 0
                except ValueError as exc:
                    self.send_json(400, {"error": str(exc)})
                    return
                try:
                    expires_at = payload.get("expiresAt")
                    expires_at = int(expires_at) if expires_at not in (None, "", 0, "0") else None
                    if expires_at is not None and expires_at <= now():
                        raise ValueError("token_expiry_must_be_future")
                except (TypeError, ValueError) as exc:
                    self.send_json(400, {"error": str(exc) or "invalid_token_expiry"})
                    return
                allowed_models = split_lines(payload.get("allowedModels", ""))
                ip_allowlist = split_lines(payload.get("ipAllowlist", ""))
                if len(allowed_models) > 200 or len(ip_allowlist) > 100:
                    self.send_json(400, {"error": "token_restriction_list_too_large"})
                    return
                created_items = []
                with sqlite3.connect(DB_PATH) as db:
                    for index in range(count):
                        raw_token = TOKEN_PREFIX + secrets.token_urlsafe(32)
                        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                        token_hint = f"{raw_token[:12]}********{raw_token[-4:]}"
                        item_name = name if count == 1 else f"{name}-{index + 1}"
                        cursor = db.execute(
                            """INSERT INTO api_tokens(user_id, name, token_hash, token_secret, token_hint, active, created_at, expires_at, token_group, quota_micros, quota_unlimited, used_micros, allowed_models, ip_allowlist)
                               VALUES (?, ?, ?, '', ?, 1, ?, ?, ?, ?, ?, 0, ?, ?)""",
                            (user[0], item_name, token_hash, token_hint, now(), expires_at, group_name, quota_micros, 1 if unlimited else 0, "\n".join(allowed_models), "\n".join(ip_allowlist)),
                        )
                        created_items.append({"id": cursor.lastrowid, "name": item_name, "token": raw_token, "hint": token_hint, "active": True, "expiresAt": expires_at})
                self.send_json(201, {"items": created_items, **(created_items[0] if count == 1 else {})})
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
                if not token_allows_model(api_user[9], model_name):
                    self.send_json(403, {"error": "model_not_allowed_for_token"})
                    return
                with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                    try:
                        db.execute("BEGIN IMMEDIATE")
                        model = fetch_model_row(db, model_name)
                        if not model or not model[6]:
                            raise ValueError("model_not_available")
                        unit = model[4]
                        price_micros = model[5]
                        if unit == "per_token":
                            quantity = input_tokens + output_tokens
                            if quantity <= 0:
                                raise ValueError("token_usage_required")
                            amount = (price_micros * quantity + 999) // 1000
                        else:
                            amount = price_micros
                        client_ip = self.headers.get("X-Forwarded-For", "").split(",")[0].strip() or self.client_address[0]
                        charge_result = bill_ledger(db, user[0], token_id, model_name, key, amount, unit, input_tokens, output_tokens, client_ip, 0, path, key)
                        db.execute("COMMIT")
                    except ValueError as exc:
                        db.execute("ROLLBACK")
                        self.send_json(402 if str(exc) in ("insufficient_balance", "token_quota_exceeded") else 400, {"error": str(exc)})
                        return
                    except sqlite3.IntegrityError:
                        db.execute("ROLLBACK")
                        self.send_json(409, {"error": "duplicate_idempotency_key"})
                        return
                self.send_json(200, {
                    "charged": micros_to_dollars(charge_result["amount_micros"]),
                    "balance": micros_to_dollars(charge_result["balance_micros"]),
                    "idempotent": charge_result["idempotent"],
                    "status": charge_result["status"],
                })
                return

            if path == "/api/admin/channels":
                admin = self.require_user(admin=True)
                if not admin:
                    return
                name = str(payload.get("name", "")).strip()
                upstream_base_url = str(payload.get("upstreamBaseUrl", "")).strip()
                upstream_api_key = str(payload.get("upstreamApiKey", "") or "").strip()
                note = str(payload.get("note", "")).strip()
                active = 1 if bool(payload.get("active", True)) else 0
                priority = int(payload.get("priority", 100) or 100)
                if not name or not upstream_base_url:
                    self.send_json(400, {"error": "name_and_upstreamBaseUrl_required"})
                    return
                with sqlite3.connect(DB_PATH) as db:
                    cursor = db.execute(
                        """INSERT INTO channels(name, upstream_base_url, upstream_api_key, active, priority, note, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (name, upstream_base_url, upstream_api_key, active, priority, note, now(), now()),
                    )
                    channel_id = cursor.lastrowid
                    updated = db.execute(
                        "SELECT id, name, upstream_base_url, upstream_api_key, active, priority, note, created_at, updated_at FROM channels WHERE id=?",
                        (channel_id,),
                    ).fetchone()
                self.send_json(201, {"channel": serialize_channel(updated)})
                return
            self.send_json(404, {"error": "not_found"})
        except Exception as exc:
            print("do_POST error:", repr(exc))
            traceback.print_exc()
            try:
                self.send_json(500, {"error": "internal_error"})
            except Exception:
                pass
        except Exception as exc:
            print("do_POST error:", repr(exc))
            traceback.print_exc()
            try:
                self.send_json(500, {"error": "internal_error"})
            except Exception:
                pass

    def do_PUT(self):
        path = urlparse(self.path).path
        if self._proxy_upstream("PUT"):
            return
        if path.startswith("/api/tokens/"):
            user = self.require_user()
            if not user:
                return
            try:
                token_id = int(path.rsplit("/", 1)[1])
                payload = self.read_json()
                active = bool(payload.get("active"))
            except (ValueError, json.JSONDecodeError):
                self.send_json(400, {"error": "invalid_token_update"})
                return
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute("UPDATE api_tokens SET active=? WHERE id=? AND user_id=?", (1 if active else 0, token_id, user[0]))
            if cursor.rowcount != 1:
                self.send_json(404, {"error": "token_not_found"})
                return
            self.send_json(200, {"id": token_id, "active": active})
            return
        if path == "/api/admin/config":
            admin = self.require_user(admin=True)
            if not admin:
                return
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            if "upstreamApiKey" not in payload:
                self.send_json(400, {"error": "upstreamApiKey_required"})
                return
            upstream_api_key = str(payload.get("upstreamApiKey", "") or "").strip()
            with sqlite3.connect(DB_PATH) as db:
                set_setting(db, "upstream_api_key", upstream_api_key)
                route = get_upstream_route(db)
            self.send_json(200, {
                "upstreamBaseUrl": route["base_url"],
                "activeChannelName": route["channel_name"],
                "upstreamApiKeySet": bool(route["api_key"]),
                "upstreamApiKeyHint": mask_secret(route["api_key"]),
            })
            return
        if path == "/api/admin/users":
            admin = self.require_user(admin=True)
            if not admin:
                return
            self.send_json(405, {"error": "method_not_allowed"})
            return
        if path.startswith("/api/admin/users/"):
            admin = self.require_user(admin=True)
            if not admin:
                return
            try:
                user_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                self.send_json(400, {"error": "invalid_user_id"})
                return
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            role = str(payload.get("role", "")).strip()
            if admin[2] == "admin" and role == "super_admin":
                self.send_json(403, {"error": "super_admin_only"})
                return
            allowed_roles = {"user", "admin"} if admin[2] == "admin" else {"user", "admin", "super_admin"}
            if role and role not in allowed_roles:
                self.send_json(400, {"error": "invalid_role"})
                return
            balance_value = payload.get("balance")
            active_value = payload.get("active")
            password_value = str(payload.get("password", "") or "").strip()
            email_value = str(payload.get("email", "") or "").strip().lower()
            with sqlite3.connect(DB_PATH) as db:
                current = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (user_id,)).fetchone()
                if not current:
                    self.send_json(404, {"error": "user_not_found"})
                    return
                new_role = role or current[3]
                new_active = current[4] if active_value is None else (1 if bool(active_value) else 0)
                new_balance = current[5]
                if balance_value is not None:
                    new_balance = dollars_to_micros(balance_value)
                updates = ["role=?", "active=?", "balance_micros=?"]
                values = [new_role, new_active, new_balance]
                if email_value:
                    updates.insert(0, "email=?")
                    values.insert(0, email_value)
                if password_value:
                    updates.append("password_hash=?")
                    values.append(hash_password(password_value))
                values.append(user_id)
                db.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=?", values)
                updated = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (user_id,)).fetchone()
            self.send_json(200, {"user": serialize_user(updated)})
            return
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

    def do_PATCH(self):
        path = urlparse(self.path).path
        if self._proxy_upstream("PATCH"):
            return
        if path.startswith("/api/admin/channels/"):
            admin = self.require_user(admin=True)
            if not admin:
                return
            try:
                channel_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                self.send_json(400, {"error": "invalid_channel_id"})
                return
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            fields = []
            values = []
            for key, column in (
                ("name", "name"),
                ("upstreamBaseUrl", "upstream_base_url"),
                ("upstreamApiKey", "upstream_api_key"),
                ("note", "note"),
                ("active", "active"),
                ("priority", "priority"),
            ):
                if key not in payload:
                    continue
                value = payload.get(key)
                if key == "active":
                    value = 1 if bool(value) else 0
                elif key == "priority":
                    value = int(value or 0)
                else:
                    value = str(value or "").strip()
                fields.append(f"{column}=?")
                values.append(value)
            if not fields:
                self.send_json(400, {"error": "no_fields_to_update"})
                return
            values.extend([now(), channel_id])
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute(
                    f"UPDATE channels SET {', '.join(fields)}, updated_at=? WHERE id=?",
                    values,
                )
                if cursor.rowcount != 1:
                    self.send_json(404, {"error": "channel_not_found"})
                    return
                updated = db.execute(
                    "SELECT id, name, upstream_base_url, upstream_api_key, active, priority, note, created_at, updated_at FROM channels WHERE id=?",
                    (channel_id,),
                ).fetchone()
            self.send_json(200, {"channel": serialize_channel(updated)})
            return
        self.send_json(404, {"error": "not_found"})

    def do_DELETE(self):
        path = urlparse(self.path).path
        if self._proxy_upstream("DELETE"):
            return
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
            db.execute("UPDATE ledger SET token_id=NULL WHERE token_id=? AND user_id=?", (token_id, user[0]))
            cursor = db.execute("DELETE FROM api_tokens WHERE id=? AND user_id=?", (token_id, user[0]))
        if cursor.rowcount != 1:
            self.send_json(404, {"error": "token_not_found"})
            return
        self.send_json(200, {"id": token_id, "deleted": True})


def main():
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("NBAPI running at http://127.0.0.1:8765")
    print(f"Super admin account: {DEFAULT_SUPER_ADMIN_USERNAME}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
