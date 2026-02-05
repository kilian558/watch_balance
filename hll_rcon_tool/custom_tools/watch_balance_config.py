"""
watch_balance_config.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that filters (kick) players based upon their language.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import os

def _env_csv(name: str) -> list:
    value = os.getenv(name, "").strip()
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _pad_list(values: list, target_len: int, fill_value) -> list:
    if len(values) >= target_len:
        return values[:target_len]
    return values + [fill_value] * (target_len - len(values))


# Discord embeds strings translations
# Available : 0 for english, 1 for french, 2 for german
LANG = _env_int("WATCH_BALANCE_LANG", 0)

_default_server_config = [
    ["https://discord.com/api/webhooks/...", True],  # Server 1
    ["https://discord.com/api/webhooks/...", False],  # Server 2
    ["https://discord.com/api/webhooks/...", False],  # Server 3
    ["https://discord.com/api/webhooks/...", False],  # Server 4
    ["https://discord.com/api/webhooks/...", False],  # Server 5
    ["https://discord.com/api/webhooks/...", False],  # Server 6
    ["https://discord.com/api/webhooks/...", False],  # Server 7
    ["https://discord.com/api/webhooks/...", False],  # Server 8
    ["https://discord.com/api/webhooks/...", False],  # Server 9
    ["https://discord.com/api/webhooks/...", False]  # Server 10
]

_env_webhooks = _env_csv("WATCH_BALANCE_WEBHOOKS")
_env_webhook_single = os.getenv("WATCH_BALANCE_WEBHOOK", "").strip()
if _env_webhook_single and not _env_webhooks:
    _env_webhooks = [_env_webhook_single]

_env_enabled_raw = _env_csv("WATCH_BALANCE_ENABLED")
_env_enabled = [_env_bool(value, True) for value in _env_enabled_raw]

if _env_webhooks:
    _target_len = max(len(_default_server_config), len(_env_webhooks))
    _webhooks = _pad_list(_env_webhooks, _target_len, "")
    _enabled = _pad_list(_env_enabled, _target_len, False)
    SERVER_CONFIG = []
    for index in range(_target_len):
        webhook = _webhooks[index]
        enabled = _enabled[index] and bool(webhook)
        SERVER_CONFIG.append([webhook, enabled])
else:
    # Dedicated Discord's channel webhook
    # ServerNumber, Webhook, Enabled
    SERVER_CONFIG = _default_server_config


# Miscellaneous (you don't have to change these)
# ----------------------------------------------

# The interval between watch turns (in seconds)
# Recommended : as the stats must be gathered for all the players,
#               requiring some amount of data from the game server,
#               you may encounter slowdowns if done too frequently.
# Default : 300
WATCH_INTERVAL_SECS = _env_int("WATCH_BALANCE_INTERVAL_SECS", 300)

# Bot name that will be displayed in CRCON "audit logs" and Discord embeds
BOT_NAME = os.getenv("WATCH_BALANCE_BOT_NAME", "CRCON_watch_balance")

# Server name to display in Discord embed
SERVER_NAME = os.getenv("WATCH_BALANCE_SERVER_NAME", "HLL Server")

# RCON API (HTTP)
RCON_API_BASE_URL = os.getenv("RCON_API_BASE_URL", "").strip()
RCON_API_TOKEN = os.getenv("RCON_API_TOKEN", "").strip()
RCON_API_TOKEN_HEADER = os.getenv("RCON_API_TOKEN_HEADER", "Authorization").strip()
RCON_API_TOKEN_PREFIX = os.getenv("RCON_API_TOKEN_PREFIX", "Bearer").strip()
RCON_API_TIMEOUT_SECS = _env_int("RCON_API_TIMEOUT_SECS", 15)
RCON_API_TEAM_ENDPOINT = os.getenv("RCON_API_TEAM_ENDPOINT", "get_team_view").strip()
RCON_API_PLAYERS_ENDPOINT = os.getenv("RCON_API_PLAYERS_ENDPOINT", "get_detailed_players").strip()

# Discord bot output (non-webhook)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
DISCORD_CHANNEL_ID = _env_int("DISCORD_CHANNEL_ID", 0)
WATCH_BALANCE_MIN_UPDATE_SECS = _env_int("WATCH_BALANCE_MIN_UPDATE_SECS", 300)

# Optional override for the state DB filename
WATCH_BALANCE_DB_PATH = os.getenv("WATCH_BALANCE_DB_PATH", "").strip()
