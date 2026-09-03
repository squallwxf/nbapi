import hashlib
import ipaddress
import json
import os
import secrets
import sqlite3
import threading
import time
import traceback
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, unquote, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


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
UPSTREAM_TIMEOUT = int(os.environ.get("NBAPI_UPSTREAM_TIMEOUT", "90"))
UPSTREAM_MAX_ATTEMPTS = int(os.environ.get("NBAPI_UPSTREAM_MAX_ATTEMPTS", "2"))
ZPAY_SUBMIT_URL = os.environ.get("NBAPI_ZPAY_SUBMIT_URL", "https://zpayz.cn/submit.php")
ZPAY_PID = os.environ.get("NBAPI_ZPAY_PID", "").strip()
ZPAY_KEY = os.environ.get("NBAPI_ZPAY_KEY", "").strip()
ZPAY_NOTIFY_URL = os.environ.get("NBAPI_ZPAY_NOTIFY_URL", "https://nbapi.win/api/payment/zpay/notify").strip()
ZPAY_RETURN_URL = os.environ.get("NBAPI_ZPAY_RETURN_URL", "https://nbapi.win/#wallet").strip()
ZPAY_CID = os.environ.get("NBAPI_ZPAY_CID", "").strip()
ZPAY_MIN_TOPUP = Decimal(os.environ.get("NBAPI_ZPAY_MIN_TOPUP", "1"))
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
    ("claude-fable-5", "Claude Fable 5", "Anthropic", "对话模型", "per_token", 0),
    ("claude-opus-4-6", "Claude Opus 4.6", "Anthropic", "对话模型", "per_token", 0),
    ("claude-opus-4-8", "Claude Opus 4.8", "Anthropic", "对话模型", "per_token", 0),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6", "Anthropic", "对话模型", "per_token", 0),
    ("gemini-3.1-flash-lite-preview", "Gemini 3.1 Flash Lite", "Google", "对话模型", "per_token", 0),
    ("gemini-3.1-pro-preview", "Gemini 3.1 Pro", "Google", "对话模型", "per_token", 0),
    ("ky-fast-720p", "可灵 Fast", "Kling", "视频生成", "per_task", 0),
    ("ky-pro-720p", "可灵 Pro", "Kling", "视频生成", "per_task", 0),
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
    ("sora-v4-480p", "Sora 4 视频", "Sora / Veo", "视频生成", "per_task", 0),
    ("sora-v4-720p", "Sora 4 视频", "Sora / Veo", "视频生成", "per_task", 0),
    ("sora-v4-1080p", "Sora 4 视频", "Sora / Veo", "视频生成", "per_task", 0),
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

# Prices are customer-facing rates: 2x the reference rates, in USD per 1M
# tokens for token models and USD per task for media models.
MODEL_PRICE_OVERRIDES = {
    "T香蕉2": ("per_task", 240000), "T香蕉pro": ("per_task", 360000), "gpt-image-2": ("per_task", 220000),
    "gpt-5.5": ("per_token", 1950000, 1950000, 11700000, 196000, 0), "gpt-5.6-sol": ("per_token", 1950000, 1950000, 11700000, 196000, 0), "gpt-5.6-terra": ("per_token", 780000, 780000, 6240000, 78000, 0),
    "claude-fable-5": ("per_token", 28800000, 28800000, 144000000, 2880000, 36000000), "claude-opus-4-6": ("per_token", 4680000, 4680000, 23400000, 468000, 5850000), "claude-opus-4-8": ("per_token", 5760000, 5760000, 28800000, 576000, 7200000), "claude-sonnet-4-6": ("per_token", 8640000, 8640000, 43200000, 864000, 10800000),
    "gemini-3.1-flash-lite-preview": ("per_token", 1200000, 1200000, 7200000, 0, 0), "gemini-3.1-pro-preview": ("per_token", 3000000, 3000000, 18000000, 300000, 0),
    "ky-fast-720p": ("per_task", 5100000), "ky-pro-720p": ("per_task", 5950000),
    "grok-video-480p": ("per_task", 800000), "grok-video-720p": ("per_task", 1000000), "grok-imagine-video-1.5-480p": ("per_task", 800000), "grok-imagine-video-1.5-720p": ("per_task", 1000000),
    "omni-flash": ("per_task", 456000), "omni-flash-1080p": ("per_task", 532000), "omni-flash-4k": ("per_task", 608000), "omni-flash-components": ("per_task", 456000), "omni-flash-components-1080p": ("per_task", 532000), "omni-flash-components-4k": ("per_task", 608000), "omni-flash-edit": ("per_task", 4920000), "omni-flash-edit-1080p": ("per_task", 6720000), "omni-flash-edit-4k": ("per_task", 9280000),
    "sora-v3-fast": ("per_task", 1000000), "sora-v3-fast-1080p": ("per_task", 1680000), "sora-v3-pro": ("per_task", 1200000), "sora-v3-pro-1080p": ("per_task", 1960000), "sora-v4-480p": ("per_task", 1310000), "sora-v4-720p": ("per_task", 1360000), "sora-v4-1080p": ("per_task", 2800000),
    "veo-3.1-lite-720": ("per_task", 960000), "veo-3.1-lite-1080": ("per_task", 1440000), "veo-3.1-lite-4k": ("per_task", 4800000), "veo-3.1-fast-720": ("per_task", 1560000), "veo-3.1-fast-1080": ("per_task", 2160000), "veo-3.1-fast-4k": ("per_task", 4224000),
    "veo-3.1-quality-720": ("per_task", 2000000), "veo-3.1-quality-1080": ("per_task", 2000000), "veo-3.1-quality-4k": ("per_task", 2000000),
}
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


def zpay_sign(params: dict[str, object], key: str) -> str:
    pairs = []
    for name in sorted(params):
        value = params[name]
        if name in ("sign", "sign_type") or value is None or str(value) == "":
            continue
        pairs.append(f"{name}={value}")
    return hashlib.md5(("&".join(pairs) + key).encode("utf-8")).hexdigest()


def zpay_signature_valid(params: dict[str, str]) -> bool:
    supplied = str(params.get("sign", "")).strip().lower()
    if not supplied or str(params.get("sign_type", "MD5")).upper() != "MD5":
        return False
    expected = zpay_sign(params, ZPAY_KEY)
    return secrets.compare_digest(supplied, expected)


def zpay_configured() -> bool:
    return bool(ZPAY_PID and ZPAY_KEY and ZPAY_NOTIFY_URL and ZPAY_RETURN_URL)


def new_merchant_order_no() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d%H%M%S") + secrets.token_hex(5)


def settle_zpay_order(params: dict[str, str], caller_ip: str):
    if not zpay_configured():
        raise ValueError("zpay_not_configured")
    if str(params.get("pid", "")).strip() != ZPAY_PID:
        raise ValueError("zpay_pid_mismatch")
    if str(params.get("trade_status", "")).strip() != "TRADE_SUCCESS":
        raise ValueError("zpay_payment_not_success")
    if not zpay_signature_valid(params):
        raise ValueError("zpay_signature_invalid")
    merchant_no = str(params.get("out_trade_no", "")).strip()
    provider_trade_no = str(params.get("trade_no", "")).strip()
    if not merchant_no or not provider_trade_no:
        raise ValueError("zpay_order_number_missing")
    try:
        notified_amount = dollars_to_micros(params.get("money"))
    except ValueError as exc:
        raise ValueError("zpay_amount_invalid") from exc
    timestamp = now()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("BEGIN IMMEDIATE")
        order = db.execute(
            "SELECT id, user_id, amount_micros, status, provider_trade_no FROM wallet_orders WHERE merchant_order_no=? AND payment_provider='zpay'",
            (merchant_no,),
        ).fetchone()
        if not order:
            raise LookupError("zpay_order_not_found")
        order_id, user_id, amount_micros, status, stored_trade_no = order
        if notified_amount != amount_micros:
            raise ValueError("zpay_amount_mismatch")
        if status == "paid":
            if stored_trade_no and stored_trade_no != provider_trade_no:
                raise ValueError("zpay_trade_number_mismatch")
            return {"idempotent": True, "orderId": order_id, "status": "paid"}
        if status != "pending":
            raise ValueError("zpay_order_status_invalid")
        reused_trade = db.execute(
            "SELECT id FROM wallet_orders WHERE provider_trade_no=? AND id<>? LIMIT 1",
            (provider_trade_no, order_id),
        ).fetchone()
        if reused_trade:
            raise ValueError("zpay_trade_number_reused")
        db.execute(
            "UPDATE users SET balance_micros=balance_micros+? WHERE id=? AND active=1",
            (amount_micros, user_id),
        )
        if db.execute("SELECT changes()").fetchone()[0] != 1:
            raise ValueError("wallet_user_not_found_or_disabled")
        db.execute(
            "INSERT INTO balance_transactions(user_id, amount_micros, type, reference_id, note, created_at) VALUES (?, ?, 'topup_zpay', ?, ?, ?)",
            (user_id, amount_micros, order_id, f"ZPAY payment {provider_trade_no} from {caller_ip}", timestamp),
        )
        db.execute(
            "UPDATE wallet_orders SET status='paid', provider_trade_no=?, paid_amount_micros=?, notify_at=?, signature_valid=1, updated_at=? WHERE id=? AND status='pending'",
            (provider_trade_no, notified_amount, timestamp, timestamp, order_id),
        )
        return {"idempotent": False, "orderId": order_id, "status": "paid"}


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
              created_at INTEGER NOT NULL,
              manager_id INTEGER REFERENCES users(id)
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
              updated_at INTEGER NOT NULL,
              input_price_micros INTEGER NOT NULL DEFAULT 0,
              output_price_micros INTEGER NOT NULL DEFAULT 0,
              cache_read_price_micros INTEGER NOT NULL DEFAULT 0,
              cache_write_price_micros INTEGER NOT NULL DEFAULT 0
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
              reserved_micros INTEGER NOT NULL DEFAULT 0,
              adjustment_micros INTEGER NOT NULL DEFAULT 0,
              cache_read_tokens INTEGER NOT NULL DEFAULT 0,
              cache_write_tokens INTEGER NOT NULL DEFAULT 0,
              usage_source TEXT NOT NULL DEFAULT '',
              UNIQUE(user_id, idempotency_key)
            );
            CREATE TABLE IF NOT EXISTS billing_reservations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              token_id INTEGER NOT NULL REFERENCES api_tokens(id),
              model_name TEXT NOT NULL REFERENCES models(name),
              idempotency_key TEXT NOT NULL,
              reserved_micros INTEGER NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('reserved', 'settled', 'refunded')),
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              UNIQUE(user_id, idempotency_key)
            );
            CREATE TABLE IF NOT EXISTS media_tasks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              token_id INTEGER NOT NULL REFERENCES api_tokens(id),
              task_id TEXT NOT NULL,
              request_id TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'submitted',
              error_message TEXT NOT NULL DEFAULT '',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              UNIQUE(user_id, task_id)
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
              health_status TEXT NOT NULL DEFAULT 'unknown',
              consecutive_failures INTEGER NOT NULL DEFAULT 0,
              last_checked_at INTEGER,
              last_success_at INTEGER,
              last_failure_at INTEGER,
              last_error TEXT NOT NULL DEFAULT '',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS wallet_orders (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              amount_micros INTEGER NOT NULL CHECK(amount_micros > 0),
              status TEXT NOT NULL CHECK(status IN ('pending','paid','rejected')) DEFAULT 'pending',
              payment_method TEXT NOT NULL DEFAULT 'manual',
              note TEXT NOT NULL DEFAULT '',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS balance_transactions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL REFERENCES users(id),
              amount_micros INTEGER NOT NULL,
              type TEXT NOT NULL,
              reference_id INTEGER,
              note TEXT NOT NULL DEFAULT '',
              created_at INTEGER NOT NULL
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
                  created_at INTEGER NOT NULL,
                  manager_id INTEGER REFERENCES users(id)
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
        if "manager_id" not in user_columns:
            db.execute("ALTER TABLE users ADD COLUMN manager_id INTEGER REFERENCES users(id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_users_manager_id ON users(manager_id)")
        wallet_columns = {row[1] for row in db.execute("PRAGMA table_info(wallet_orders)")}
        for column, definition in (
            ("merchant_order_no", "TEXT NOT NULL DEFAULT ''"),
            ("provider_trade_no", "TEXT NOT NULL DEFAULT ''"),
            ("payment_provider", "TEXT NOT NULL DEFAULT 'manual'"),
            ("paid_amount_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("notify_at", "INTEGER"),
            ("signature_valid", "INTEGER NOT NULL DEFAULT 0"),
        ):
            if column not in wallet_columns:
                db.execute(f"ALTER TABLE wallet_orders ADD COLUMN {column} {definition}")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_wallet_orders_merchant_order_no ON wallet_orders(merchant_order_no) WHERE merchant_order_no <> ''")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_wallet_orders_provider_trade_no ON wallet_orders(provider_trade_no) WHERE provider_trade_no <> ''")
        db.execute("CREATE INDEX IF NOT EXISTS idx_billing_reservations_status ON billing_reservations(status)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_media_tasks_status ON media_tasks(status)")
        cleanup_stale_reservations(db)
        columns = {row[1] for row in db.execute("PRAGMA table_info(ledger)")}
        if "token_id" not in columns:
            db.execute("ALTER TABLE ledger ADD COLUMN token_id INTEGER REFERENCES api_tokens(id)")
        for column, definition in (
            ("client_ip", "TEXT NOT NULL DEFAULT ''"),
            ("latency_ms", "INTEGER NOT NULL DEFAULT 0"),
            ("request_path", "TEXT NOT NULL DEFAULT ''"),
            ("request_id", "TEXT NOT NULL DEFAULT ''"),
            ("reserved_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("adjustment_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("cache_read_tokens", "INTEGER NOT NULL DEFAULT 0"),
            ("cache_write_tokens", "INTEGER NOT NULL DEFAULT 0"),
            ("usage_source", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in columns:
                db.execute(f"ALTER TABLE ledger ADD COLUMN {column} {definition}")
        model_columns = {row[1] for row in db.execute("PRAGMA table_info(models)")}
        for column, definition in (
            ("input_price_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("output_price_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("cache_read_price_micros", "INTEGER NOT NULL DEFAULT 0"),
            ("cache_write_price_micros", "INTEGER NOT NULL DEFAULT 0"),
        ):
            if column not in model_columns:
                db.execute(f"ALTER TABLE models ADD COLUMN {column} {definition}")
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
        channel_columns = {row[1] for row in db.execute("PRAGMA table_info(channels)")}
        for column, definition in (
            ("health_status", "TEXT NOT NULL DEFAULT 'unknown'"),
            ("consecutive_failures", "INTEGER NOT NULL DEFAULT 0"),
            ("last_checked_at", "INTEGER"),
            ("last_success_at", "INTEGER"),
            ("last_failure_at", "INTEGER"),
            ("last_error", "TEXT NOT NULL DEFAULT ''"),
        ):
            if column not in channel_columns:
                db.execute(f"ALTER TABLE channels ADD COLUMN {column} {definition}")
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
        if get_setting(db, "pricing_schema_version") != "4":
            for name, pricing in MODEL_PRICE_OVERRIDES.items():
                unit, price, *token_prices = pricing
                input_price, output_price, cache_read, cache_write = (token_prices + [0, 0, 0, 0])[:4]
                db.execute("UPDATE models SET billing_unit=?, price_micros=?, input_price_micros=?, output_price_micros=?, cache_read_price_micros=?, cache_write_price_micros=?, updated_at=? WHERE name=?", (unit, price, input_price, output_price, cache_read, cache_write, timestamp, name))
            set_setting(db, "pricing_schema_version", "4")
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


def extract_response_payload(body: bytes):
    """Extract the final JSON response, including usage from streaming SSE."""
    payload = try_parse_json_bytes(body)
    if isinstance(payload, dict):
        return payload
    try:
        lines = body.decode("utf-8", "replace").splitlines()
    except Exception:
        return None
    fallback = None
    for line in reversed(lines):
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if not data or data == "[DONE]":
            continue
        try:
            candidate = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            if extract_usage_object(candidate) is not None:
                return candidate
            if fallback is None:
                fallback = candidate
    return fallback


def extract_usage_object(payload):
    if not isinstance(payload, dict):
        return None
    if isinstance(payload.get("usage"), dict):
        return payload["usage"]
    if isinstance(payload.get("usageMetadata"), dict):
        return payload["usageMetadata"]
    return None


def extract_usage_counts(payload) -> tuple[int, int]:
    usage = extract_usage_object(payload)
    if usage is None:
        return 0, 0
    candidates = (
        ("inputTokens", "input_tokens", "prompt_tokens", "promptTokens", "promptTokenCount", "inputTokenCount"),
        ("outputTokens", "output_tokens", "completion_tokens", "completionTokens", "candidatesTokenCount", "outputTokenCount"),
        ("totalTokens", "total_tokens", "totalTokens", "totalTokenCount"),
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
    if input_tokens is None or output_tokens is None:
        return 0, 0
    return input_tokens, output_tokens


def extract_cache_usage(payload) -> tuple[int, int]:
    usage = extract_usage_object(payload)
    if usage is None:
        return 0, 0
    details = usage.get("prompt_tokens_details") if isinstance(usage.get("prompt_tokens_details"), dict) else {}
    input_details = usage.get("input_tokens_details") if isinstance(usage.get("input_tokens_details"), dict) else {}
    cache_read = details.get("cached_tokens")
    if cache_read is None:
        cache_read = details.get("cache_read_input_tokens")
    if cache_read is None:
        cache_read = input_details.get("cached_tokens")
    if cache_read is None:
        cache_read = usage.get("cache_read_input_tokens")
    if cache_read is None:
        cache_read = usage.get("cacheReadInputTokens")
    if cache_read is None:
        cache_read = usage.get("cachedContentTokenCount", 0)
    cache_write = usage.get("cache_creation_input_tokens", usage.get("cache_write_input_tokens", usage.get("cacheWriteInputTokens", 0))) or 0
    try:
        return max(0, int(cache_read)), max(0, int(cache_write))
    except (TypeError, ValueError):
        return 0, 0


def has_separate_usage_counts(payload) -> bool:
    usage = extract_usage_object(payload)
    if usage is None:
        return False
    input_keys = ("inputTokens", "input_tokens", "prompt_tokens", "promptTokens", "promptTokenCount", "inputTokenCount")
    output_keys = ("outputTokens", "output_tokens", "completion_tokens", "completionTokens", "candidatesTokenCount", "outputTokenCount")

    def has_valid_value(keys):
        for key in keys:
            if key not in usage:
                continue
            try:
                return int(usage[key]) >= 0
            except (TypeError, ValueError):
                return False
        return False

    return has_valid_value(input_keys) and has_valid_value(output_keys)


def calculate_token_charge_micros(model_row, response_payload):
    """Calculate a token charge only from authoritative upstream usage."""
    if not has_separate_usage_counts(response_payload):
        raise ValueError("upstream_usage_unavailable")
    input_tokens, output_tokens = extract_usage_counts(response_payload)
    cache_read_tokens, cache_write_tokens = extract_cache_usage(response_payload)
    input_price = model_row[7] if model_row[7] > 0 else model_row[5]
    output_price = model_row[8] if model_row[8] > 0 else input_price
    usage = extract_usage_object(response_payload) or {}
    has_openai_cache_details = isinstance(usage.get("prompt_tokens_details"), dict) or isinstance(usage.get("input_tokens_details"), dict)
    billable_input_tokens = max(0, input_tokens - cache_read_tokens) if has_openai_cache_details else input_tokens
    amount_micros = (
        input_price * billable_input_tokens
        + output_price * output_tokens
        + model_row[9] * cache_read_tokens
        + model_row[10] * cache_write_tokens
        + 999_999
    ) // 1_000_000
    return amount_micros, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens


def get_upstream_routes(db):
    rows = db.execute(
        "SELECT id, name, upstream_base_url, upstream_api_key FROM channels WHERE active=1 AND (consecutive_failures<3 OR last_failure_at<?) ORDER BY priority ASC, id ASC",
        (now() - 300,),
    ).fetchall()
    routes = []
    for row in rows:
        base_url = str(row[2] or "").strip() or UPSTREAM
        if base_url.lower().endswith("/v1") or base_url.lower().endswith("/v1beta"):
            base_url = base_url.rsplit("/", 1)[0]
        routes.append({"channel_id": row[0], "channel_name": row[1], "base_url": base_url.rstrip("/"), "api_key": str(row[3] or "").strip() or get_setting(db, "upstream_api_key", "")})
    return routes


def get_upstream_route(db):
    routes = get_upstream_routes(db)
    if routes:
        return routes[0]
    return {
        "channel_id": None,
        "channel_name": None,
        "base_url": UPSTREAM.rstrip("/"),
        "api_key": get_setting(db, "upstream_api_key", ""),
    }


def update_channel_health(channel_id: int | None, success: bool, error: str = "") -> None:
    if channel_id is None:
        return
    timestamp = now()
    with sqlite3.connect(DB_PATH) as db:
        if success:
            db.execute("UPDATE channels SET health_status='healthy', consecutive_failures=0, last_checked_at=?, last_success_at=?, last_error='' WHERE id=?", (timestamp, timestamp, channel_id))
        else:
            db.execute("UPDATE channels SET health_status='unhealthy', consecutive_failures=consecutive_failures+1, last_checked_at=?, last_failure_at=?, last_error=? WHERE id=?", (timestamp, timestamp, str(error)[:500], channel_id))


def fetch_model_row(db, model_name: str):
    return db.execute(
        "SELECT name, provider_label, provider, kind, billing_unit, price_micros, active, input_price_micros, output_price_micros, cache_read_price_micros, cache_write_price_micros FROM models WHERE name=?",
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


def cleanup_stale_reservations(db, ttl_seconds: int = 24 * 60 * 60):
    cutoff = now() - ttl_seconds
    rows = db.execute(
        "SELECT id, user_id, token_id, reserved_micros FROM billing_reservations WHERE status='reserved' AND updated_at<?",
        (cutoff,),
    ).fetchall()
    for reservation_id, user_id, token_id, reserved_micros in rows:
        db.execute("UPDATE users SET balance_micros=balance_micros+? WHERE id=?", (reserved_micros, user_id))
        db.execute("UPDATE api_tokens SET used_micros=MAX(0, used_micros-?) WHERE id=?", (reserved_micros, token_id))
        db.execute("UPDATE billing_reservations SET status='refunded', updated_at=? WHERE id=? AND status='reserved'", (now(), reservation_id))


def reserve_billing(db, user_id: int, token_id: int, model_name: str, idempotency_key: str, amount_micros: int):
    """Atomically reserve wallet and token quota before an upstream call."""
    existing_ledger = db.execute(
        "SELECT amount_micros, status FROM ledger WHERE user_id=? AND idempotency_key=?",
        (user_id, idempotency_key),
    ).fetchone()
    if existing_ledger:
        return {"idempotent": True, "settled": True, "amount_micros": existing_ledger[0], "status": existing_ledger[1]}
    existing = db.execute(
        "SELECT id, reserved_micros, status FROM billing_reservations WHERE user_id=? AND idempotency_key=?",
        (user_id, idempotency_key),
    ).fetchone()
    if existing:
        if existing[2] == "reserved":
            return {"idempotent": True, "settled": False, "amount_micros": existing[1], "reservation_id": existing[0]}
        raise ValueError("duplicate_idempotency_key")
    amount_micros = max(0, int(amount_micros))
    balance_row = db.execute("SELECT balance_micros FROM users WHERE id=? AND active=1", (user_id,)).fetchone()
    if not balance_row:
        raise ValueError("user_not_found")
    if balance_row[0] < amount_micros:
        raise ValueError("insufficient_balance")
    token_row = db.execute(
        "SELECT quota_micros, quota_unlimited, used_micros FROM api_tokens WHERE id=? AND user_id=? AND active=1",
        (token_id, user_id),
    ).fetchone()
    if not token_row:
        raise ValueError("invalid_or_inactive_api_key")
    if not token_row[1] and token_row[2] + amount_micros > token_row[0]:
        raise ValueError("token_quota_exceeded")
    timestamp = now()
    db.execute("UPDATE users SET balance_micros=balance_micros-? WHERE id=?", (amount_micros, user_id))
    db.execute("UPDATE api_tokens SET used_micros=used_micros+? WHERE id=?", (amount_micros, token_id))
    cursor = db.execute(
        "INSERT INTO billing_reservations(user_id, token_id, model_name, idempotency_key, reserved_micros, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'reserved', ?, ?)",
        (user_id, token_id, model_name, idempotency_key, amount_micros, timestamp, timestamp),
    )
    return {"idempotent": False, "settled": False, "amount_micros": amount_micros, "reservation_id": cursor.lastrowid}


def settle_billing(db, user_id: int, token_id: int, model_name: str, idempotency_key: str, actual_micros: int, billing_unit: str, input_tokens: int, output_tokens: int, client_ip: str, latency_ms: int, request_path: str, request_id: str, cache_read_tokens: int = 0, cache_write_tokens: int = 0, usage_source: str = ""):
    reservation = db.execute(
        "SELECT id, reserved_micros, status FROM billing_reservations WHERE user_id=? AND idempotency_key=?",
        (user_id, idempotency_key),
    ).fetchone()
    if not reservation:
        return bill_ledger(db, user_id, token_id, model_name, idempotency_key, actual_micros, billing_unit, input_tokens, output_tokens, client_ip, latency_ms, request_path, request_id)
    if reservation[2] == "settled":
        existing = db.execute("SELECT amount_micros, status FROM ledger WHERE user_id=? AND idempotency_key=?", (user_id, idempotency_key)).fetchone()
        balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user_id,)).fetchone()[0]
        return {"idempotent": True, "amount_micros": existing[0], "balance_micros": balance, "status": existing[1]}
    if reservation[2] == "refunded":
        raise ValueError("billing_reservation_already_refunded")
    actual_micros = max(0, int(actual_micros))
    delta = actual_micros - reservation[1]
    if delta > 0:
        # The request was already authorized by the reservation. If actual
        # usage is higher, settle the difference atomically. Allowing the
        # wallet to go negative prevents an upstream-successful request from
        # becoming an unbilled business loss.
        db.execute("UPDATE users SET balance_micros=balance_micros-? WHERE id=?", (delta, user_id))
        db.execute("UPDATE api_tokens SET used_micros=used_micros+? WHERE id=?", (delta, token_id))
    elif delta < 0:
        refund = -delta
        db.execute("UPDATE users SET balance_micros=balance_micros+? WHERE id=?", (refund, user_id))
        db.execute("UPDATE api_tokens SET used_micros=MAX(0, used_micros-?) WHERE id=?", (refund, token_id))
    timestamp = now()
    db.execute(
        "INSERT INTO ledger(user_id, model_name, idempotency_key, amount_micros, billing_unit, input_tokens, output_tokens, status, created_at, token_id, client_ip, latency_ms, request_path, request_id, reserved_micros, adjustment_micros, cache_read_tokens, cache_write_tokens, usage_source) VALUES (?, ?, ?, ?, ?, ?, ?, 'charged', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, model_name, idempotency_key, actual_micros, billing_unit, input_tokens, output_tokens, timestamp, token_id, client_ip, latency_ms, request_path, request_id, reservation[1], delta, cache_read_tokens, cache_write_tokens, usage_source),
    )
    db.execute("UPDATE billing_reservations SET status='settled', updated_at=? WHERE id=?", (timestamp, reservation[0]))
    balance = db.execute("SELECT balance_micros FROM users WHERE id=?", (user_id,)).fetchone()[0]
    return {"idempotent": False, "amount_micros": actual_micros, "balance_micros": balance, "status": "charged"}


def refund_billing(db, user_id: int, idempotency_key: str):
    reservation = db.execute(
        "SELECT id, token_id, reserved_micros, status FROM billing_reservations WHERE user_id=? AND idempotency_key=?",
        (user_id, idempotency_key),
    ).fetchone()
    if not reservation or reservation[3] != "reserved":
        return False
    refund = reservation[2]
    db.execute("UPDATE users SET balance_micros=balance_micros+? WHERE id=?", (refund, user_id))
    db.execute("UPDATE api_tokens SET used_micros=MAX(0, used_micros-?) WHERE id=?", (refund, reservation[1]))
    db.execute("UPDATE billing_reservations SET status='refunded', updated_at=? WHERE id=?", (now(), reservation[0]))
    return True


def settle_wallet_order(order_id: int, action: str):
    """Settle a manual top-up exactly once inside one SQLite transaction."""
    if action not in ("approve", "reject"):
        raise ValueError("invalid_wallet_order_action")
    timestamp = now()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("BEGIN IMMEDIATE")
        order = db.execute(
            "SELECT id, user_id, amount_micros, status, payment_method FROM wallet_orders WHERE id=?",
            (order_id,),
        ).fetchone()
        if not order:
            raise LookupError("wallet_order_not_found")
        order_id, user_id, amount_micros, status, payment_method = order
        if status == "paid":
            if action == "approve":
                return {"id": order_id, "status": status, "idempotent": True}
            raise ValueError("wallet_order_already_paid")
        if status == "rejected":
            if action == "reject":
                return {"id": order_id, "status": status, "idempotent": True}
            raise ValueError("wallet_order_already_rejected")
        if amount_micros <= 0:
            raise ValueError("wallet_order_amount_invalid")
        if action == "approve":
            db.execute(
                "UPDATE users SET balance_micros=balance_micros+? WHERE id=? AND active=1",
                (amount_micros, user_id),
            )
            if db.execute("SELECT changes()").fetchone()[0] != 1:
                raise ValueError("wallet_user_not_found_or_disabled")
            db.execute(
                "INSERT INTO balance_transactions(user_id, amount_micros, type, reference_id, note, created_at) VALUES (?, ?, 'topup_manual', ?, ?, ?)",
                (user_id, amount_micros, order_id, f"manual wallet top-up via {payment_method}", timestamp),
            )
            new_status = "paid"
        else:
            new_status = "rejected"
        db.execute(
            "UPDATE wallet_orders SET status=?, updated_at=? WHERE id=? AND status='pending'",
            (new_status, timestamp, order_id),
        )
        return {"id": order_id, "status": new_status, "idempotent": False}


def extract_task_id(payload) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("task_id", "taskId", "id"):
        value = str(payload.get(key, "") or "").strip()
        if value:
            return value
    for container_key in ("data", "result"):
        container = payload.get(container_key)
        if isinstance(container, dict):
            value = extract_task_id(container)
            if value:
                return value
        if isinstance(container, list):
            for item in container:
                value = extract_task_id(item)
                if value:
                    return value
    return ""


def extract_task_status(payload) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("status", "state"):
        value = str(payload.get(key, "") or "").strip().lower()
        if value:
            return value
    return ""


def settle_media_task_status(db, user_id: int, token_id: int, task_id: str, payload) -> bool:
    task = db.execute(
        "SELECT id, request_id, status FROM media_tasks WHERE user_id=? AND token_id=? AND task_id=?",
        (user_id, token_id, task_id),
    ).fetchone()
    if not task:
        return False
    status = extract_task_status(payload)
    if status in ("succeeded", "completed", "success", "done"):
        db.execute("UPDATE media_tasks SET status='completed', updated_at=? WHERE id=? AND status='submitted'", (now(), task[0]))
        return False
    if status not in ("failed", "error", "cancelled", "canceled", "rejected") or task[2] != "submitted":
        return False
    ledger = db.execute(
        "SELECT id, amount_micros, status FROM ledger WHERE user_id=? AND request_id=?",
        (user_id, task[1]),
    ).fetchone()
    if not ledger or ledger[2] != "charged":
        db.execute("UPDATE media_tasks SET status='failed', updated_at=? WHERE id=? AND status='submitted'", (now(), task[0]))
        return False
    amount = ledger[1]
    db.execute("UPDATE users SET balance_micros=balance_micros+? WHERE id=?", (amount, user_id))
    db.execute("UPDATE api_tokens SET used_micros=MAX(0, used_micros-?) WHERE id=?", (amount, token_id))
    db.execute("UPDATE ledger SET status='refunded' WHERE id=? AND status='charged'", (ledger[0],))
    db.execute("UPDATE media_tasks SET status='refunded', error_message=?, updated_at=? WHERE id=? AND status='submitted'", (str(payload.get("error", "task_failed"))[:500] if isinstance(payload, dict) else "task_failed", now(), task[0]))
    return True


def record_media_task(db, user_id: int, token_id: int, task_id: str, request_id: str):
    if not task_id:
        return
    db.execute(
        "INSERT OR IGNORE INTO media_tasks(user_id, token_id, task_id, request_id, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'submitted', ?, ?)",
        (user_id, token_id, task_id, request_id, now(), now()),
    )


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
    result = {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "role": row[3],
        "active": bool(row[4]),
        "balance": micros_to_dollars(row[5]),
        "createdAt": row[6],
    }
    if len(row) > 7:
        result.update({
            "managerId": row[7],
            "managerUsername": row[8] or "",
            "weekRecharge": micros_to_dollars(row[9] or 0) if len(row) > 9 else "0.000000",
            "monthRecharge": micros_to_dollars(row[10] or 0) if len(row) > 10 else "0.000000",
        })
    return result


def beijing_period_starts(timestamp=None):
    current = datetime.fromtimestamp(timestamp or now(), ZoneInfo("Asia/Shanghai"))
    today = current.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    return int(week_start.timestamp()), int(month_start.timestamp())


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
        "healthStatus": row[9],
        "consecutiveFailures": row[10],
        "lastCheckedAt": row[11],
        "lastSuccessAt": row[12],
        "lastFailureAt": row[13],
        "lastError": row[14],
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

    def send_text(self, status: int, value: str) -> None:
        body = value.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
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
        idempotency_key = (
            str(self.headers.get("Idempotency-Key", "")).strip()
            or secrets.token_urlsafe(24)
        )
        if len(idempotency_key) > 128:
            self.send_json(400, {"error": "idempotency_key_too_long"})
            return True

        if method in ("POST", "PUT", "PATCH", "DELETE") and not model_name:
            self.send_json(400, {"error": "model_required"})
            return True

        with sqlite3.connect(DB_PATH) as db:
            routes = get_upstream_routes(db)
            if not routes:
                routes = [get_upstream_route(db)]
            if not any(route["api_key"] for route in routes):
                self.send_json(503, {"error": "upstream_api_key_not_configured"})
                return True

            model_row = None
            reservation_created = False
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
                reserve_amount = model_row[5]
                if model_row[4] == "per_token":
                    estimated_input = max(1, len(json.dumps(payload or {}, ensure_ascii=False)) // 4)
                    estimated_output = 0
                    for key in ("max_tokens", "maxTokens", "max_completion_tokens", "maxCompletionTokens"):
                        try:
                            estimated_output = max(0, int((payload or {}).get(key, 0) or 0))
                        except (TypeError, ValueError):
                            estimated_output = 0
                        if estimated_output:
                            break
                    reserve_amount = (
                        (model_row[7] if model_row[7] > 0 else model_row[5]) * estimated_input
                        + (model_row[8] if model_row[8] > 0 else (model_row[7] if model_row[7] > 0 else model_row[5])) * estimated_output
                        + 999_999
                    ) // 1_000_000
                try:
                    db.execute("BEGIN IMMEDIATE")
                    reservation = reserve_billing(db, api_user[1], api_user[0], model_name, idempotency_key, reserve_amount)
                    db.execute("COMMIT")
                    reservation_created = not reservation.get("idempotent")
                except ValueError as exc:
                    db.execute("ROLLBACK")
                    self.send_json(402 if str(exc) in ("insufficient_balance", "token_quota_exceeded") else 400, {"error": str(exc)})
                    return True

        resp_status, resp_headers, resp_body = 502, {}, b""
        routes = [route for route in routes if route["api_key"]][:max(1, UPSTREAM_MAX_ATTEMPTS)]
        for attempt, route in enumerate(routes):
            upstream_url = f"{route['base_url']}{path}" + (f"?{parsed.query}" if parsed.query else "")
            upstream_headers = {key: value for key, value in self.headers.items() if key.lower() not in HOP_BY_HOP_HEADERS | {"host", "content-length", "authorization"}}
            upstream_headers["Authorization"] = f"Bearer {route['api_key']}"
            if body and "content-type" not in {key.lower() for key in upstream_headers}:
                upstream_headers["Content-Type"] = self.headers.get("Content-Type", "application/json")
            try:
                request = Request(upstream_url, data=body if method in ("POST", "PUT", "PATCH", "DELETE") else None, headers=upstream_headers, method=method)
                with urlopen(request, timeout=UPSTREAM_TIMEOUT) as response:
                    resp_status, resp_headers, resp_body = response.status, dict(response.headers.items()), response.read()
                update_channel_health(route["channel_id"], True)
                break
            except HTTPError as exc:
                resp_status, resp_headers, resp_body = exc.code, dict(exc.headers.items()) if exc.headers else {}, exc.read() or b""
                if resp_status < 500:
                    update_channel_health(route["channel_id"], True)
                    break
                update_channel_health(route["channel_id"], False, f"HTTP {resp_status}")
            except (URLError, TimeoutError, OSError) as exc:
                resp_status, resp_headers, resp_body = 502, {}, b""
                update_channel_health(route["channel_id"], False, str(getattr(exc, "reason", exc)))
            if attempt + 1 < len(routes):
                continue

        if not (200 <= resp_status < 300):
            if model_row and reservation_created:
                with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                    db.execute("BEGIN IMMEDIATE")
                    refund_billing(db, api_user[1], idempotency_key)
                    db.execute("COMMIT")
            self._send_raw_response(resp_status, resp_headers, resp_body)
            return True

        response_payload = extract_response_payload(resp_body)
        if method == "GET" and (path.startswith("/v1/images/tasks/") or path.startswith("/v1/videos/")):
            task_id = unquote(path.rstrip("/").rsplit("/", 1)[-1]).strip()
            if task_id:
                with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                    db.execute("BEGIN IMMEDIATE")
                    refunded = settle_media_task_status(db, api_user[1], api_user[0], task_id, response_payload)
                    db.execute("COMMIT")
                if refunded:
                    resp_headers["X-NBAPI-Refunded"] = "1"
        if model_row:
            billing_unit = model_row[4]
            price_micros = model_row[5]
            input_tokens = 0
            output_tokens = 0
            if billing_unit == "per_token":
                # Never silently charge an estimate for a token-priced model.
                # New API settles from authoritative upstream usage; doing the
                # same here prevents both accidental overcharging and free
                # calls caused by an unparseable response.
                if not has_separate_usage_counts(response_payload):
                    if reservation_created:
                        with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                            db.execute("BEGIN IMMEDIATE")
                            refund_billing(db, api_user[1], idempotency_key)
                            db.execute("COMMIT")
                    self.send_json(502, {"error": "upstream_usage_unavailable", "message": "上游未返回可核验的输入和补全 Token 用量，未执行扣费。"})
                    return True
                amount_micros, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens = calculate_token_charge_micros(model_row, response_payload)
                usage_source = "gemini" if extract_usage_object(response_payload) is response_payload.get("usageMetadata") else "openai_compatible"
            else:
                amount_micros = price_micros
                cache_read_tokens = 0
                cache_write_tokens = 0
                usage_source = "per_task"

            with sqlite3.connect(DB_PATH, timeout=10, isolation_level=None) as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                    charge_result = settle_billing(db, api_user[1], api_user[0], model_name, idempotency_key, amount_micros, billing_unit, input_tokens, output_tokens, client_ip, round((time.perf_counter() - started_at) * 1000), path, idempotency_key, cache_read_tokens, cache_write_tokens, usage_source)
                    if billing_unit == "per_task":
                        record_media_task(db, api_user[1], api_user[0], extract_task_id(response_payload), idempotency_key)
                    db.execute("COMMIT")
                except ValueError as exc:
                    db.execute("ROLLBACK")
                    self.send_json(502, {"error": str(exc), "message": "上游调用已完成，但结算未完成，请保留 Request ID 供管理员对账。", "requestId": idempotency_key})
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
        if path == "/api/payment/zpay/notify":
            params = {key: values[-1] for key, values in parse_qs(urlparse(self.path).query, keep_blank_values=True).items()}
            try:
                settle_zpay_order(params, self._client_ip())
            except (ValueError, LookupError) as exc:
                print(f"ZPAY notify rejected: {exc}")
                self.send_text(400, "fail")
                return
            self.send_text(200, "success")
            return
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
            self.send_json(403, {"error": "permission_removed"})
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
            week_start, month_start = beijing_period_starts()
            with sqlite3.connect(DB_PATH) as db:
                params = []
                filters = []
                if admin[2] == "admin":
                    filters.append("u.manager_id=?")
                    params.append(admin[0])
                if search:
                    filters.append("(lower(u.username) LIKE ? OR lower(u.email) LIKE ? OR lower(u.role) LIKE ? OR lower(COALESCE(m.username,'')) LIKE ?)")
                    like = f"%{search}%"
                    params.extend([like, like, like, like])
                where = f"WHERE {' AND '.join(filters)}" if filters else ""
                total = db.execute(f"SELECT COUNT(*) FROM users u LEFT JOIN users m ON m.id=u.manager_id {where}", params).fetchone()[0]
                rows = db.execute(
                    f"""SELECT u.id, u.username, u.email, u.role, u.active, u.balance_micros, u.created_at,
                              u.manager_id, COALESCE(m.username,''),
                              (SELECT COALESCE(SUM(o.amount_micros),0) FROM wallet_orders o WHERE o.user_id=u.id AND o.status='paid' AND o.created_at>=?),
                              (SELECT COALESCE(SUM(o.amount_micros),0) FROM wallet_orders o WHERE o.user_id=u.id AND o.status='paid' AND o.created_at>=?)
                       FROM users u LEFT JOIN users m ON m.id=u.manager_id {where}
                       ORDER BY u.id DESC LIMIT ? OFFSET ?""",
                    [week_start, month_start, *params, page_size, offset],
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
            self.send_json(403, {"error": "permission_removed"})
            return
        if path == "/api/models":
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute("SELECT name, provider_label, provider, kind, billing_unit, price_micros, active, input_price_micros, output_price_micros, cache_read_price_micros, cache_write_price_micros FROM models ORDER BY rowid").fetchall()
            self.send_json(200, {"models": [
                {"name": r[0], "providerLabel": r[1], "provider": r[2], "kind": r[3], "billingUnit": r[4], "price": micros_to_dollars(r[5]), "inputPrice": micros_to_dollars(r[7] or r[5]), "outputPrice": micros_to_dollars(r[8] or r[5]), "cacheReadPrice": micros_to_dollars(r[9]), "cacheWritePrice": micros_to_dollars(r[10]), "active": bool(r[6])}
                for r in rows
            ]})
            return
        if path == "/api/dashboard":
            user = self.current_user()
            current_time = time.localtime()
            today_start = int(time.mktime((current_time.tm_year, current_time.tm_mon, current_time.tm_mday, 0, 0, 0, 0, 0, -1)))
            month_start = int(time.mktime((current_time.tm_year, current_time.tm_mon, 1, 0, 0, 0, 0, 0, -1)))
            with sqlite3.connect(DB_PATH) as db:
                model_count = db.execute("SELECT COUNT(*) FROM models WHERE active=1").fetchone()[0]
                channel_count = db.execute("SELECT COUNT(*) FROM channels WHERE active=1").fetchone()[0]
                if user:
                    today_requests = db.execute("SELECT COUNT(*) FROM ledger WHERE user_id=? AND created_at>=?", (user[0], today_start)).fetchone()[0]
                    month_amount = db.execute("SELECT COALESCE(SUM(amount_micros),0) FROM ledger WHERE user_id=? AND created_at>=?", (user[0], month_start)).fetchone()[0]
                    avg_latency = db.execute("SELECT COALESCE(AVG(latency_ms),0) FROM ledger WHERE user_id=? AND created_at>=? AND latency_ms>0", (user[0], today_start)).fetchone()[0]
                    balance = user[3]
                else:
                    today_requests = 0
                    month_amount = 0
                    avg_latency = 0
                    balance = 0
            self.send_json(200, {"models": model_count, "channels": channel_count, "todayRequests": today_requests, "monthAmount": micros_to_dollars(month_amount), "balance": micros_to_dollars(balance), "avgLatencyMs": round(avg_latency or 0)})
            return
        if path == "/api/wallet":
            user = self.require_user()
            if not user:
                return
            with sqlite3.connect(DB_PATH) as db:
                orders = db.execute("SELECT id, amount_micros, status, payment_method, payment_provider, merchant_order_no, note, created_at, updated_at FROM wallet_orders WHERE user_id=? ORDER BY id DESC LIMIT 50", (user[0],)).fetchall()
                transactions = db.execute("SELECT id, amount_micros, type, reference_id, note, created_at FROM balance_transactions WHERE user_id=? ORDER BY id DESC LIMIT 50", (user[0],)).fetchall()
            self.send_json(200, {"balance": micros_to_dollars(user[3]), "orders": [{"id": r[0], "amount": micros_to_dollars(r[1]), "status": r[2], "paymentMethod": r[3], "paymentProvider": r[4], "merchantOrderNo": r[5], "note": r[6], "createdAt": r[7], "updatedAt": r[8]} for r in orders], "transactions": [{"id": r[0], "amount": micros_to_dollars(r[1]), "type": r[2], "referenceId": r[3], "note": r[4], "createdAt": r[5]} for r in transactions]})
            return
        if path == "/api/admin/wallet/orders":
            admin = self.require_user(admin=True)
            if not admin:
                return
            if admin[2] != "super_admin":
                self.send_json(403, {"error": "super_admin_only"})
                return
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute(
                    "SELECT o.id, u.username, o.amount_micros, o.status, o.payment_method, o.note, o.created_at, o.updated_at FROM wallet_orders o JOIN users u ON u.id=o.user_id ORDER BY CASE o.status WHEN 'pending' THEN 0 ELSE 1 END, o.id DESC LIMIT 100"
                ).fetchall()
            self.send_json(200, {"items": [{
                "id": r[0], "username": r[1], "amount": micros_to_dollars(r[2]), "status": r[3],
                "paymentMethod": r[4], "note": r[5], "createdAt": r[6], "updatedAt": r[7]
            } for r in rows]})
            return
        if path == "/api/admin/managers":
            admin = self.require_user(admin=True)
            if not admin:
                return
            if admin[2] != "super_admin":
                self.send_json(403, {"error": "super_admin_only"})
                return
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute("SELECT id, username, role FROM users WHERE role IN ('admin','super_admin') AND active=1 ORDER BY role DESC, username COLLATE NOCASE").fetchall()
            self.send_json(200, {"items": [{"id": r[0], "username": r[1], "role": r[2]} for r in rows]})
            return
        if path == "/api/admin/manager-customers":
            admin = self.require_user(admin=True)
            if not admin:
                return
            if admin[2] != "super_admin":
                self.send_json(403, {"error": "super_admin_only"})
                return
            query = parse_qs(urlparse(self.path).query)
            try:
                manager_id = int(query.get("managerId", ["0"])[0])
            except ValueError:
                manager_id = 0
            if not manager_id:
                self.send_json(400, {"error": "manager_id_required"})
                return
            week_start, month_start = beijing_period_starts()
            with sqlite3.connect(DB_PATH) as db:
                rows = db.execute("""SELECT u.id, u.username, u.email, u.role, u.active, u.balance_micros, u.created_at,
                    u.manager_id, COALESCE(m.username,''),
                    (SELECT COALESCE(SUM(o.amount_micros),0) FROM wallet_orders o WHERE o.user_id=u.id AND o.status='paid' AND o.created_at>=?),
                    (SELECT COALESCE(SUM(o.amount_micros),0) FROM wallet_orders o WHERE o.user_id=u.id AND o.status='paid' AND o.created_at>=?)
                    FROM users u LEFT JOIN users m ON m.id=u.manager_id WHERE u.manager_id=? ORDER BY u.id DESC""", (week_start, month_start, manager_id)).fetchall()
            self.send_json(200, {"items": [serialize_user(row) for row in rows]})
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
                        f"SELECT COUNT(*), COALESCE(SUM(CASE WHEN l.status='charged' THEN l.amount_micros ELSE 0 END),0), COALESCE(SUM(l.input_tokens),0), COALESCE(SUM(l.output_tokens),0) FROM ledger l LEFT JOIN api_tokens t ON t.id=l.token_id WHERE {where}", params
                    ).fetchone()
                    rows = db.execute(
                        f"SELECT l.id, l.model_name, l.amount_micros, l.billing_unit, l.input_tokens, l.output_tokens, l.status, l.created_at, l.token_id, COALESCE(t.name,''), COALESCE(t.token_hint,''), COALESCE(t.token_group,'default'), COALESCE(l.request_id,l.idempotency_key), COALESCE(l.client_ip,''), COALESCE(l.latency_ms,0), COALESCE(l.request_path,''), COALESCE(l.reserved_micros,0), COALESCE(l.adjustment_micros,0), COALESCE(l.cache_read_tokens,0), COALESCE(l.cache_write_tokens,0), COALESCE(l.usage_source,'') FROM ledger l LEFT JOIN api_tokens t ON t.id=l.token_id WHERE {where} ORDER BY l.id DESC LIMIT ? OFFSET ?",
                        [*params, page_size, (page - 1) * page_size],
                    ).fetchall()
                self.send_json(200, {"items": [{
                    "id": r[0], "model": r[1], "amount": micros_to_dollars(r[2] if r[6] == "charged" else 0), "chargedAmount": micros_to_dollars(r[2]), "billingUnit": r[3], "inputTokens": r[4], "outputTokens": r[5], "status": r[6], "createdAt": r[7], "tokenId": r[8], "tokenName": r[9] or "未关联令牌", "tokenHint": r[10], "tokenGroup": r[11], "requestId": r[12], "ip": r[13] or "-", "latencyMs": r[14], "path": r[15], "reserved": micros_to_dollars(r[16]), "adjustment": micros_to_dollars(r[17]), "cacheReadTokens": r[18], "cacheWriteTokens": r[19], "usageSource": r[20] or "-"
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
            if path == "/api/payment/zpay/notify":
                length = int(self.headers.get("Content-Length", "0"))
                if length < 0 or length > MAX_REQUEST_BODY:
                    self.send_text(413, "fail")
                    return
                body = self.rfile.read(length) if length else b""
                params = {key: values[-1] for key, values in parse_qs(body.decode("utf-8", "replace"), keep_blank_values=True).items()}
                try:
                    settle_zpay_order(params, self._client_ip())
                except (ValueError, LookupError) as exc:
                    print(f"ZPAY notify rejected: {exc}")
                    self.send_text(400, "fail")
                    return
                self.send_text(200, "success")
                return
            try:
                payload = self.read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
                return

            if path.startswith("/api/admin/wallet/orders/"):
                admin = self.require_user(admin=True)
                if not admin:
                    return
                if admin[2] != "super_admin":
                    self.send_json(403, {"error": "super_admin_only"})
                    return
                try:
                    order_id = int(path.rsplit("/", 1)[1])
                    action = str(payload.get("action", "")).strip().lower()
                    result = settle_wallet_order(order_id, action)
                except (TypeError, ValueError, LookupError) as exc:
                    error = str(exc)
                    status = 404 if error == "wallet_order_not_found" else 400
                    self.send_json(status, {"error": error})
                    return
                self.send_json(200, result)
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
                designated_admin = str(payload.get("designatedAdmin", "")).strip()
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
                        manager_id = None
                        manager_username = ""
                        if designated_admin:
                            manager = db.execute("SELECT id, username FROM users WHERE lower(username)=lower(?) AND role IN ('admin','super_admin') AND active=1", (designated_admin,)).fetchone()
                            if manager:
                                manager_id, manager_username = manager
                        cursor = db.execute(
                            "INSERT INTO users(username, email, password_hash, role, active, balance_micros, created_at, manager_id) VALUES (?, ?, ?, 'user', 1, ?, ?, ?)",
                            (username, email, hash_password(password), 0, timestamp, manager_id),
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
                        "managerId": manager_id,
                        "managerUsername": manager_username,
                    },
                    "managerMatched": bool(manager_id),
                    "managerUsername": manager_username,
                })
                return

            if path == "/api/admin/users":
                admin = self.require_user(admin=True)
                if not admin:
                    return
                username = str(payload.get("username", "")).strip()
                password = str(payload.get("password", ""))
                if not (3 <= len(username) <= 32):
                    self.send_json(400, {"error": "username_length_invalid"})
                    return
                if not username.replace("_", "").replace("-", "").isalnum():
                    self.send_json(400, {"error": "username_format_invalid"})
                    return
                if len(password) < 6:
                    self.send_json(400, {"error": "password_too_short"})
                    return
                try:
                    with sqlite3.connect(DB_PATH) as db:
                        cursor = db.execute(
                            "INSERT INTO users(username, email, password_hash, role, active, balance_micros, created_at, manager_id) VALUES (?, '', ?, 'user', 1, 0, ?, ?)",
                            (username, hash_password(password), now(), admin[0] if admin[2] == "admin" else None),
                        )
                        row = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (cursor.lastrowid,)).fetchone()
                except sqlite3.IntegrityError:
                    self.send_json(409, {"error": "username_already_exists"})
                    return
                self.send_json(201, {"user": serialize_user(row)})
                return

            if path == "/api/admin/manager-customers":
                admin = self.require_user(admin=True)
                if not admin:
                    return
                if admin[2] != "super_admin":
                    self.send_json(403, {"error": "super_admin_only"})
                    return
                try:
                    user_id = int(payload.get("userId"))
                    manager_id = payload.get("managerId")
                    manager_id = int(manager_id) if manager_id not in (None, "", 0, "0") else None
                    action = str(payload.get("action", "assign")).strip().lower()
                except (TypeError, ValueError):
                    self.send_json(400, {"error": "invalid_assignment"})
                    return
                if action not in ("assign", "unassign"):
                    self.send_json(400, {"error": "invalid_assignment_action"})
                    return
                if action == "unassign":
                    manager_id = None
                with sqlite3.connect(DB_PATH) as db:
                    user = db.execute("SELECT id, role FROM users WHERE id=?", (user_id,)).fetchone()
                    if not user or user[1] != "user":
                        self.send_json(404, {"error": "customer_user_not_found"})
                        return
                    if manager_id is not None:
                        manager = db.execute("SELECT id FROM users WHERE id=? AND role IN ('admin','super_admin') AND active=1", (manager_id,)).fetchone()
                        if not manager:
                            self.send_json(400, {"error": "manager_not_found"})
                            return
                    db.execute("UPDATE users SET manager_id=? WHERE id=?", (manager_id, user_id))
                    updated = db.execute("SELECT id, username, email, role, active, balance_micros, created_at, manager_id, COALESCE((SELECT username FROM users m WHERE m.id=users.manager_id),'') FROM users WHERE id=?", (user_id,)).fetchone()
                self.send_json(200, {"user": serialize_user(updated)})
                return

            if path == "/api/wallet/orders":
                user = self.require_user()
                if not user:
                    return
                try:
                    amount_micros = dollars_to_micros(payload.get("amount"))
                except ValueError as exc:
                    self.send_json(400, {"error": str(exc)})
                    return
                if amount_micros < dollars_to_micros(ZPAY_MIN_TOPUP):
                    self.send_json(400, {"error": "minimum_topup_not_met", "minimum": str(ZPAY_MIN_TOPUP)})
                    return
                if not zpay_configured():
                    self.send_json(503, {"error": "zpay_not_configured"})
                    return
                payment_method = str(payload.get("paymentMethod", "alipay")).strip().lower()
                if payment_method not in ("alipay", "wxpay"):
                    self.send_json(400, {"error": "unsupported_payment_method"})
                    return
                timestamp = now()
                with sqlite3.connect(DB_PATH) as db:
                    cursor = db.execute(
                        "INSERT INTO wallet_orders(user_id, amount_micros, status, payment_method, payment_provider, merchant_order_no, note, created_at, updated_at) VALUES (?, ?, 'pending', ?, 'zpay', ?, ?, ?, ?)",
                        (user[0], amount_micros, payment_method, "", "", timestamp, timestamp),
                    )
                    order_id = cursor.lastrowid
                    merchant_no = f"{datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d%H%M%S')}{order_id:08d}"
                    db.execute("UPDATE wallet_orders SET merchant_order_no=? WHERE id=?", (merchant_no, order_id))
                params = {
                    "name": "NBAPI 账户充值",
                    "money": micros_to_dollars(amount_micros).rstrip("0").rstrip("."),
                    "type": payment_method,
                    "out_trade_no": merchant_no,
                    "notify_url": ZPAY_NOTIFY_URL,
                    "pid": ZPAY_PID,
                    "param": str(order_id),
                    "return_url": ZPAY_RETURN_URL,
                    "sign_type": "MD5",
                }
                if ZPAY_CID:
                    params["cid"] = ZPAY_CID
                params["sign"] = zpay_sign(params, ZPAY_KEY)
                self.send_json(201, {"id": order_id, "amount": micros_to_dollars(amount_micros), "status": "pending", "paymentUrl": f"{ZPAY_SUBMIT_URL}?{urlencode(params)}", "merchantOrderNo": merchant_no})
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
                # This legacy endpoint accepted client-supplied usage and was
                # therefore forgeable. Billing is now performed only inside
                # the authenticated upstream proxy after parsing its response.
                self.send_json(410, {"error": "billing_endpoint_removed", "message": "请直接调用 /v1 接口，系统会依据上游返回的真实用量自动计费。"})
                return

            if path == "/api/admin/channels":
                self.send_json(403, {"error": "permission_removed"})
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
            self.send_json(403, {"error": "permission_removed"})
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
            if admin[2] != "super_admin":
                self.send_json(403, {"error": "super_admin_only"})
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
            balance_value = payload.get("balance")
            if balance_value is None:
                self.send_json(400, {"error": "balance_required"})
                return
            with sqlite3.connect(DB_PATH) as db:
                current = db.execute("SELECT id, username, email, role, active, balance_micros, created_at FROM users WHERE id=?", (user_id,)).fetchone()
                if not current:
                    self.send_json(404, {"error": "user_not_found"})
                    return
                new_balance = dollars_to_micros(balance_value)
                db.execute("UPDATE users SET balance_micros=? WHERE id=?", (new_balance, user_id))
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
        if admin[2] != "super_admin":
            self.send_json(403, {"error": "super_admin_only"})
            return
        name = path[len(prefix):]
        try:
            payload = self.read_json()
            billing_unit = payload.get("billingUnit")
            if billing_unit not in ("per_task", "per_token"):
                raise ValueError("billingUnit must be per_task or per_token")
            price_micros = dollars_to_micros(payload.get("price"))
            input_price = dollars_to_micros(payload.get("inputPrice", payload.get("price")))
            output_price = dollars_to_micros(payload.get("outputPrice", payload.get("price")))
            cache_read_price = dollars_to_micros(payload.get("cacheReadPrice", 0))
            cache_write_price = dollars_to_micros(payload.get("cacheWritePrice", 0))
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE models SET price_micros=?, billing_unit=?, input_price_micros=?, output_price_micros=?, cache_read_price_micros=?, cache_write_price_micros=?, updated_at=? WHERE name=?", (price_micros, billing_unit, input_price, output_price, cache_read_price, cache_write_price, now(), name))
            if cursor.rowcount != 1:
                self.send_json(404, {"error": "model_not_found"})
                return
        self.send_json(200, {"model": name, "price": micros_to_dollars(price_micros), "inputPrice": micros_to_dollars(input_price), "outputPrice": micros_to_dollars(output_price), "cacheReadPrice": micros_to_dollars(cache_read_price), "cacheWritePrice": micros_to_dollars(cache_write_price), "billingUnit": billing_unit})

    def do_PATCH(self):
        path = urlparse(self.path).path
        if self._proxy_upstream("PATCH"):
            return
        if path.startswith("/api/admin/channels/"):
            self.send_json(403, {"error": "permission_removed"})
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
