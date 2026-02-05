"""
watch_balance.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import asyncio
import json
import logging
import os
import pathlib
import sqlite3
import ssl
import time
import sys
from datetime import datetime, timezone
from time import sleep
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import discord

# Handle both direct execution and module execution
if __name__ == "__main__":
    # Direct execution - add parent directory to path
    import sys
    import pathlib
    ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from hll_rcon_tool.custom_tools import common_functions
    from hll_rcon_tool.custom_tools.common_translations import TRANSL
    from hll_rcon_tool.custom_tools import watch_balance_config as config
else:
    # Module execution - use relative imports
    from . import common_functions
    from .common_translations import TRANSL
    from . import watch_balance_config as config

logger = logging.getLogger("rcon")


def team_avg(
    all_players: list,
    observed_team: str,
    observed_parameter: str,
    total_count: int
) -> float:
    """
    Divide the sum of "observed_parameter" values from all the players in "team" by "total_count"
    ie :
    t1_lvl_avg: float = team_avg(all_players, "allies", "level", t1_count)
    """
    if total_count == 0:
        return 0
    return_value = sum(
        player.get(observed_parameter, 0)
        for player in all_players
        if player.get("team") == observed_team
    ) / total_count
    if return_value == 0:
        return 0
    return return_value


def level_cursor(
    t1_lvl_avg: float,
    t2_lvl_avg: float,
    slots_tot: int = 44  # Prefer a pair value, or the 'middle pin' won't be in middle
) -> str:
    """
    Returns a full gauge :
    ie (slots_tot = 40) : "`100 50% [--------------------|--------------------] 100 50%`"
    ie (slots_tot = 40) : "`200 67% [-------------------->>>>>>>|-------------] 100 33%`"
    ie (slots_tot = 40) : "` 50 25% [----------|<<<<<<<<<<--------------------] 150 75%`"
    """
    t1_avg_pct: float = (t1_lvl_avg / (t1_lvl_avg + t2_lvl_avg)) * 100
    t1_avg_pct_slots: int = round(t1_avg_pct / (100 / slots_tot))
    t2_avg_pct_slots: int = slots_tot - t1_avg_pct_slots

    if t1_avg_pct_slots > round(slots_tot / 2):
        t1_below50pct_str: str = "-" * round(slots_tot / 2)
        t1_over50pct_str: str = ">" * (t1_avg_pct_slots - round(slots_tot / 2))
        t2_below50pct_str: str = "-" * t2_avg_pct_slots
        t2_over50pct_str: str = ""
    else:
        t1_below50pct_str: str = "-" * t1_avg_pct_slots
        t1_over50pct_str: str = ""
        t2_below50pct_str: str = "-" * round(slots_tot / 2)
        t2_over50pct_str: str = "<" * (t2_avg_pct_slots - round(slots_tot / 2))

    return(
        f"`{round(t1_lvl_avg):>3} {round(t1_avg_pct):>2}%"
        f" [{t1_below50pct_str}{t1_over50pct_str}|{t2_over50pct_str}{t2_below50pct_str}] "
        f"{round(t2_lvl_avg):>3} {round(100 - t1_avg_pct):>2}%`"
    )


def level_pop_distribution(
    all_players: list,
    t1_count: int,
    t2_count: int,
    slots_tot: int = 36  # Prefer a pair value, or the 'middle pin' won't be in middle
) -> str:
    """
    returns a multilines (5) string representing a graph of level tiers
    """
    if t1_count == 0 or t2_count == 0:
        return "`No data`"

    t1_l1_count: int = sum(1 for player in all_players if player["team"] == "allies" and 1 <= player["level"] < 30)
    t1_l2_count: int = sum(1 for player in all_players if player["team"] == "allies" and 30 <= player["level"] < 60)
    t1_l3_count: int = sum(1 for player in all_players if player["team"] == "allies" and 60 <= player["level"] < 125)
    t1_l4_count: int = sum(1 for player in all_players if player["team"] == "allies" and 125 <= player["level"] < 250)
    t1_l5_count: int = sum(1 for player in all_players if player["team"] == "allies" and 250 <= player["level"] <= 500)

    t1_l1_slots: int = round((t1_l1_count * slots_tot) / (2 * t1_count))
    t1_l2_slots: int = round((t1_l2_count * slots_tot) / (2 * t1_count))
    t1_l3_slots: int = round((t1_l3_count * slots_tot) / (2 * t1_count))
    t1_l4_slots: int = round((t1_l4_count * slots_tot) / (2 * t1_count))
    t1_l5_slots: int = round((t1_l5_count * slots_tot) / (2 * t1_count))

    t2_l1_count: int = sum(1 for player in all_players if player["team"] == "axis" and 1 <= player["level"] < 30)
    t2_l2_count: int = sum(1 for player in all_players if player["team"] == "axis" and 30 <= player["level"] < 60)
    t2_l3_count: int = sum(1 for player in all_players if player["team"] == "axis" and 60 <= player["level"] < 125)
    t2_l4_count: int = sum(1 for player in all_players if player["team"] == "axis" and 125 <= player["level"] < 250)
    t2_l5_count: int = sum(1 for player in all_players if player["team"] == "axis" and 250 <= player["level"] <= 500)

    t2_l1_slots: int = round((t2_l1_count * slots_tot) / (2 * t2_count))
    t2_l2_slots: int = round((t2_l2_count * slots_tot) / (2 * t2_count))
    t2_l3_slots: int = round((t2_l3_count * slots_tot) / (2 * t2_count))
    t2_l4_slots: int = round((t2_l4_count * slots_tot) / (2 * t2_count))
    t2_l5_slots: int = round((t2_l5_count * slots_tot) / (2 * t2_count))

    return_str = (
        # level 5
        f"`250-500: {t1_l5_count:>2} {round((t1_l5_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l5_slots) * ' '}{t1_l5_slots * 'â– '}"
        f"|{t2_l5_slots * 'â– '}{round((slots_tot / 2) - t2_l5_slots) * ' '}]"
        f" {t2_l5_count:>2} {round((t2_l5_count * 100) / t2_count):>3}%`\n"
        # level 4
        f"`125-249: {t1_l4_count:>2} {round((t1_l4_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l4_slots) * ' '}{t1_l4_slots * 'â– '}"
        f"|{t2_l4_slots * 'â– '}{round((slots_tot / 2) - t2_l4_slots) * ' '}]"
        f" {t2_l4_count:>2} {round((t2_l4_count * 100) / t2_count):>3}%`\n"
        # level 3
        f"` 60-124: {t1_l3_count:>2} {round((t1_l3_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l3_slots) * ' '}{t1_l3_slots * 'â– '}"
        f"|{t2_l3_slots * 'â– '}{round((slots_tot / 2) - t2_l3_slots) * ' '}]"
        f" {t2_l3_count:>2} {round((t2_l3_count * 100) / t2_count):>3}%`\n"
        # level 2
        f"` 30- 59: {t1_l2_count:>2} {round((t1_l2_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l2_slots) * ' '}{t1_l2_slots * 'â– '}"
        f"|{t2_l2_slots * 'â– '}{round((slots_tot / 2) - t2_l2_slots) * ' '}]"
        f" {t2_l2_count:>2} {round((t2_l2_count * 100) / t2_count):>3}%`\n"
        # level 1
        f"`  1- 29: {t1_l1_count:>2} {round((t1_l1_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l1_slots) * ' '}{t1_l1_slots * 'â– '}"
        f"|{t2_l1_slots * 'â– '}{round((slots_tot / 2) - t2_l1_slots) * ' '}]"
        f" {t2_l1_count:>2} {round((t2_l1_count * 100) / t2_count):>3}%`"
    )

    return return_str


def _api_headers() -> dict:
    headers = {"Accept": "application/json"}
    if config.RCON_API_TOKEN:
        token_prefix = config.RCON_API_TOKEN_PREFIX
        token_value = (
            f"{token_prefix} {config.RCON_API_TOKEN}"
            if token_prefix
            else config.RCON_API_TOKEN
        )
        if config.RCON_API_TOKEN_HEADER:
            headers[config.RCON_API_TOKEN_HEADER] = token_value
    return headers


def _api_get(endpoint: str) -> dict:
    if not config.RCON_API_BASE_URL:
        raise RuntimeError("RCON_API_BASE_URL is not set")

    base_url = config.RCON_API_BASE_URL.rstrip("/")
    url = f"{base_url}/api/{endpoint}"
    request = Request(url, headers=_api_headers(), method="GET")
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        with urlopen(request, timeout=config.RCON_API_TIMEOUT_SECS, context=ssl_context) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)
    except (HTTPError, URLError, json.JSONDecodeError) as exc:
        logger.exception("RCON API request failed for %s: %s", url, exc)
        raise


def _api_result(payload):
    if isinstance(payload, dict) and "result" in payload:
        return payload["result"]
    return payload


def _get_nested_stat(container: dict, key: str, default: int = 0) -> int:
    for candidate in (
        container,
        container.get("stats", {}),
        container.get("scores", {}),
        container.get("score", {})
    ):
        if isinstance(candidate, dict) and key in candidate:
            return candidate.get(key, default) or default
    return default


def _normalize_team_value(value: str) -> str:
    if not value:
        return ""
    lowered = str(value).strip().lower()
    if lowered in ("allies", "allied", "ally", "alliedforces"):
        return "allies"
    if lowered in ("axis", "german", "germans"):
        return "axis"
    return lowered


def _normalize_players(players_payload) -> list:
    if isinstance(players_payload, dict):
        players = players_payload.get("players", [])
    else:
        players = players_payload

    if not isinstance(players, list):
        return []

    normalized = []
    for player in players:
        if not isinstance(player, dict):
            continue
        team = player.get("team")
        if isinstance(team, dict):
            team = team.get("name")
        team = _normalize_team_value(team)

        level = player.get("level")
        if level is None:
            level = player.get("rank")
        if level is None:
            level = player.get("player_level")

        normalized.append(
            {
                "team": team,
                "role": player.get("role", ""),
                "level": int(level or 0),
                "kills": int(_get_nested_stat(player, "kills")),
                "deaths": int(_get_nested_stat(player, "deaths")),
                "combat": int(_get_nested_stat(player, "combat")),
                "offense": int(_get_nested_stat(player, "offense")),
                "defense": int(_get_nested_stat(player, "defense")),
                "support": int(_get_nested_stat(player, "support"))
            }
        )
    return normalized


def _normalize_teams(team_payload) -> list:
    if isinstance(team_payload, dict):
        if "teams" in team_payload and isinstance(team_payload["teams"], list):
            return team_payload["teams"]
        if "allies" in team_payload or "axis" in team_payload:
            teams = []
            if "allies" in team_payload:
                teams.append({"allies": team_payload["allies"]})
            if "axis" in team_payload:
                teams.append({"axis": team_payload["axis"]})
            return teams
    if isinstance(team_payload, list):
        return team_payload
    return []


def fetch_team_view_stats() -> tuple[list, list]:
    team_view_payload = _api_get(config.RCON_API_TEAM_ENDPOINT)
    players_payload = _api_get(config.RCON_API_PLAYERS_ENDPOINT)
    all_teams = _normalize_teams(_api_result(team_view_payload))
    all_players = _normalize_players(_api_result(players_payload))
    return all_teams, all_players


def _get_team_stat(team_data: dict, key: str) -> int:
    return int(_get_nested_stat(team_data, key))


def build_embed(all_teams: list, all_players: list) -> Optional[discord.Embed]:
    # Gather data
    t1_count = 0
    t2_count = 0
    t1_lvl_avg = 0.0
    t2_lvl_avg = 0.0
    t1_kills = 0
    t2_kills = 0
    t1_deaths = 0
    t2_deaths = 0
    t1_combat = 0
    t2_combat = 0
    t1_off = 0
    t2_off = 0
    t1_def = 0
    t2_def = 0
    t1_support = 0
    t2_support = 0

    for team in all_teams:
        if "allies" in team:
            data = team["allies"]
            t1_count = int(data.get("count", data.get("player_count", 0)) or 0)
            t1_lvl_avg = team_avg(all_players, "allies", "level", t1_count)
            t1_kills = _get_team_stat(data, "kills")
            t1_deaths = _get_team_stat(data, "deaths")
            t1_combat = _get_team_stat(data, "combat")
            t1_off = _get_team_stat(data, "offense")
            t1_def = _get_team_stat(data, "defense")
            t1_support = _get_team_stat(data, "support")
        elif "axis" in team:
            data = team["axis"]
            t2_count = int(data.get("count", data.get("player_count", 0)) or 0)
            t2_lvl_avg = team_avg(all_players, "axis", "level", t2_count)
            t2_kills = _get_team_stat(data, "kills")
            t2_deaths = _get_team_stat(data, "deaths")
            t2_combat = _get_team_stat(data, "combat")
            t2_off = _get_team_stat(data, "offense")
            t2_def = _get_team_stat(data, "defense")
            t2_support = _get_team_stat(data, "support")

    if t1_lvl_avg == 0 or t2_lvl_avg == 0:
        logger.info(
            "Bad data : either Allies or Axis average level is 0. Waiting for %s mins...",
            round((config.WATCH_INTERVAL_SECS / 60), 2)
        )
        return None

    if t1_count == 0 or t2_count == 0:
        logger.info(
            "Bad data : either Allies or Axis player count is 0. Waiting for %s mins...",
            round((config.WATCH_INTERVAL_SECS / 60), 2)
        )
        return None

    # Gather data : officers
    t1_officers_lvl_tot = 0
    t1_officers_count = 0
    t2_officers_lvl_tot = 0
    t2_officers_count = 0
    for player in all_players:
        if player["role"] in ("commander", "officer", "tankcommander", "spotter"):
            if player["team"] == "allies":
                t1_officers_lvl_tot += player["level"]
                t1_officers_count += 1
            elif player["team"] == "axis":
                t2_officers_lvl_tot += player["level"]
                t2_officers_count += 1

    if t1_officers_count != 0 and t2_officers_count != 0:
        t1_officers_lvl_avg = t1_officers_lvl_tot / t1_officers_count
        t2_officers_lvl_avg = t2_officers_lvl_tot / t2_officers_count
    else:
        t1_officers_lvl_avg = 0
        t2_officers_lvl_avg = 0

    # Discord embed title
    avg_diff_ratio = max(t1_lvl_avg, t2_lvl_avg) / min(t1_lvl_avg, t2_lvl_avg)
    embed_title = f"{TRANSL['ratio'][config.LANG]} : {str(round(avg_diff_ratio, 2))}"

    # Average level (all players) : title
    all_lvl_avg = (t1_lvl_avg + t2_lvl_avg) / 2
    all_lvl_avg_title = f"{TRANSL['level'][config.LANG]} ({TRANSL['avg'][config.LANG]}) : {round(all_lvl_avg)}"

    all_lvl_graph = level_cursor(
        t1_lvl_avg=t1_lvl_avg,
        t2_lvl_avg=t2_lvl_avg
    )

    # Average level (officers) : title
    if t1_officers_count != 0 and t2_officers_count != 0:
        all_officers_lvl_avg = (
            (t1_officers_lvl_tot + t2_officers_lvl_tot)
            / (t1_officers_count + t2_officers_count)
        )
        all_officers_lvl_avg_title = (
            f"{TRANSL['level'][config.LANG]} {TRANSL['officers'][config.LANG]} "
            f"({TRANSL['avg'][config.LANG]}) : {round(all_officers_lvl_avg)}"
        )

        all_officers_lvl_graph = level_cursor(
            t1_lvl_avg=t1_officers_lvl_avg,
            t2_lvl_avg=t2_officers_lvl_avg
        )

    # level population : title
    all_lvl_pop_title = f"{TRANSL['level'][config.LANG]} {TRANSL['distribution'][config.LANG]}"

    # Teams stats
    all_lvl_pop_text = level_pop_distribution(
        all_players=all_players,
        t1_count=t1_count,
        t2_count=t2_count
    )

    # col1
    col1_embed_title = f"{TRANSL['stats'][config.LANG]}"
    transl_tot_moy = f"({TRANSL['tot'][config.LANG]}/{TRANSL['avg'][config.LANG]})"
    col1_embed_text = (
        f"{TRANSL['players'][config.LANG]}\n\n"
        f"{TRANSL['kills'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['deaths'][config.LANG]} {transl_tot_moy}\n\n"
        f"{TRANSL['combat'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['offense'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['defense'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['support'][config.LANG]} {transl_tot_moy}"
    )

    # col2
    # col3
    t1_kills_str, t2_kills_str = common_functions.bold_the_highest(t1_kills, t2_kills)
    t1_deaths_str, t2_deaths_str = common_functions.bold_the_highest(t1_deaths, t2_deaths)
    t1_combat_str, t2_combat_str = common_functions.bold_the_highest(t1_combat, t2_combat)
    t1_off_str, t2_off_str = common_functions.bold_the_highest(t1_off, t2_off)
    t1_def_str, t2_def_str = common_functions.bold_the_highest(t1_def, t2_def)
    t1_support_str, t2_support_str = common_functions.bold_the_highest(t1_support, t2_support)

    # col2
    col2_embed_title = TRANSL["allies"][config.LANG]
    col2_embed_text = (
        f"{str(t1_count)}\n\n"
        f"{t1_kills_str} / {str(round(team_avg(all_players, 'allies', 'kills', t1_count)))}\n"
        f"{t1_deaths_str} / {str(round(team_avg(all_players, 'allies', 'deaths', t1_count)))}\n\n"
        f"{t1_combat_str} / {str(round(team_avg(all_players, 'allies', 'combat', t1_count)))}\n"
        f"{t1_off_str} / {str(round(team_avg(all_players, 'allies', 'offense', t1_count)))}\n"
        f"{t1_def_str} / {str(round(team_avg(all_players, 'allies', 'defense', t1_count)))}\n"
        f"{t1_support_str} / {str(round(team_avg(all_players, 'allies', 'support', t1_count)))}\n"
    )

    # col3
    col3_embed_title = TRANSL["axis"][config.LANG]
    col3_embed_text = (
        f"{str(t2_count)}\n\n"
        f"{t2_kills_str} / {str(round(team_avg(all_players, 'axis', 'kills', t2_count)))}\n"
        f"{t2_deaths_str} / {str(round(team_avg(all_players, 'axis', 'deaths', t2_count)))}\n\n"
        f"{t2_combat_str} / {str(round(team_avg(all_players, 'axis', 'combat', t2_count)))}\n"
        f"{t2_off_str} / {str(round(team_avg(all_players, 'axis', 'offense', t2_count)))}\n"
        f"{t2_def_str} / {str(round(team_avg(all_players, 'axis', 'defense', t2_count)))}\n"
        f"{t2_support_str} / {str(round(team_avg(all_players, 'axis', 'support', t2_count)))}\n"
    )

    # Log
    logger.info(
        "%s : %s - %s : (%s) %s ; (%s) %s - %s : (%s) %s ; (%s) %s",
        TRANSL['ratio'][config.LANG],
        str(round(avg_diff_ratio, 2)),
        TRANSL['players'][config.LANG],
        TRANSL['allies'][config.LANG],
        str(round(t1_lvl_avg, 2)),
        TRANSL['axis'][config.LANG],
        str(round(t2_lvl_avg, 2)),
        TRANSL['officers'][config.LANG],
        TRANSL['allies'][config.LANG],
        str(round(t1_officers_lvl_avg, 2)),
        TRANSL['axis'][config.LANG],
        str(round(t2_officers_lvl_avg, 2))
    )

    embed = discord.Embed(
        title=embed_title,
        url=common_functions.DISCORD_EMBED_AUTHOR_URL,
        color=int(
            common_functions.green_to_red(value=avg_diff_ratio, min_value=1, max_value=2),
            base=16
        )
    )
    embed.set_author(
        name=config.BOT_NAME,
        url=common_functions.DISCORD_EMBED_AUTHOR_URL,
        icon_url=common_functions.DISCORD_EMBED_AUTHOR_ICON_URL
    )
    embed.add_field(name=all_lvl_avg_title, value=all_lvl_graph, inline=False)
    if t1_officers_count != 0 and t2_officers_count != 0:
        embed.add_field(
            name=all_officers_lvl_avg_title,
            value=all_officers_lvl_graph,
            inline=False
        )
    embed.add_field(name=all_lvl_pop_title, value=all_lvl_pop_text, inline=False)
    embed.add_field(name=col1_embed_title, value=col1_embed_text, inline=True)
    embed.add_field(name=col2_embed_title, value=col2_embed_text, inline=True)
    embed.add_field(name=col3_embed_title, value=col3_embed_text, inline=True)
    embed.set_footer(text="Last Updated")
    embed.timestamp = datetime.now(tz=timezone.utc)

    return embed


def _state_db_connect(db_path: pathlib.Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS watch_balance_state ("
        "channel_id INTEGER PRIMARY KEY, "
        "message_id INTEGER NOT NULL, "
        "updated_at INTEGER NOT NULL"
        ")"
    )
    conn.commit()
    return conn


def _state_get(conn: sqlite3.Connection, channel_id: int) -> Tuple[Optional[int], Optional[int]]:
    cursor = conn.execute(
        "SELECT message_id, updated_at FROM watch_balance_state WHERE channel_id = ?",
        (channel_id,)
    )
    row = cursor.fetchone()
    if not row:
        return None, None
    return int(row[0]), int(row[1])


def _state_set(conn: sqlite3.Connection, channel_id: int, message_id: int, updated_at: int) -> None:
    conn.execute(
        "INSERT INTO watch_balance_state (channel_id, message_id, updated_at) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT(channel_id) DO UPDATE SET "
        "message_id = excluded.message_id, "
        "updated_at = excluded.updated_at",
        (channel_id, message_id, updated_at)
    )
    conn.commit()


async def send_or_edit_embed(channel: discord.TextChannel, embed: discord.Embed, conn: sqlite3.Connection) -> None:
    if channel.id == 0:
        raise RuntimeError("DISCORD_CHANNEL_ID is not set")

    last_message_id, last_updated = _state_get(conn, channel.id)
    now = int(time.time())
    if last_updated and now - last_updated < config.WATCH_BALANCE_MIN_UPDATE_SECS:
        return

    if last_message_id:
        try:
            message = await channel.fetch_message(last_message_id)
            await message.edit(embed=embed)
            _state_set(conn, channel.id, message.id, now)
            return
        except discord.NotFound:
            logger.info("Previous message not found, sending a new one.")
        except discord.Forbidden:
            logger.exception("Missing permissions to edit message.")
        except discord.HTTPException:
            logger.exception("Failed to edit message.")

    message = await channel.send(embed=embed)
    _state_set(conn, channel.id, message.id, now)


async def watch_balance_loop(client: discord.Client, conn: sqlite3.Connection) -> None:
    while True:
        try:
            if not config.RCON_API_BASE_URL:
                logger.info("RCON_API_BASE_URL not set, skipping this cycle.")
                await asyncio.sleep(config.WATCH_INTERVAL_SECS)
                continue
            if config.DISCORD_CHANNEL_ID == 0:
                logger.info("DISCORD_CHANNEL_ID not set, skipping this cycle.")
                await asyncio.sleep(config.WATCH_INTERVAL_SECS)
                continue
            loop = asyncio.get_running_loop()
            all_teams, all_players = await loop.run_in_executor(None, fetch_team_view_stats)
            if len(all_teams) < 2:
                logger.info(
                    "Less than 2 teams ingame. Waiting for %s mins...",
                    round((config.WATCH_INTERVAL_SECS / 60), 1)
                )
                await asyncio.sleep(config.WATCH_INTERVAL_SECS)
                continue

            embed = build_embed(all_teams, all_players)
            if embed is None:
                await asyncio.sleep(config.WATCH_INTERVAL_SECS)
                continue

            channel = client.get_channel(config.DISCORD_CHANNEL_ID)
            if channel is None:
                channel = await client.fetch_channel(config.DISCORD_CHANNEL_ID)

            await send_or_edit_embed(channel, embed, conn)
        except Exception:
            logger.exception("Watch balance loop failure.")

        await asyncio.sleep(config.WATCH_INTERVAL_SECS)


async def run_bot() -> None:
    if not config.DISCORD_BOT_TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set")

    root_path = os.getenv("BALANCE_WATCH_DATA_PATH", "/data")
    if config.WATCH_BALANCE_DB_PATH:
        db_path = pathlib.Path(config.WATCH_BALANCE_DB_PATH)
    else:
        db_path = pathlib.Path(root_path) / pathlib.Path("watch_balance.db")
    conn = _state_db_connect(db_path)

    intents = discord.Intents.none()
    client = discord.Client(intents=intents)

    started = False

    @client.event
    async def on_ready():
        nonlocal started
        if started:
            return
        started = True
        logger.info("Discord bot connected as %s", client.user)
        client.loop.create_task(watch_balance_loop(client, conn))

    await client.start(config.DISCORD_BOT_TOKEN)


# Launching and running (infinite loop)
if __name__ == "__main__":
    # Initial pause : wait to be sure the CRCON is fully started
    sleep(60)
    logger.info(
        "\n-------------------------------------------------------------------------------\n"
        "%s (started)\n"
        "-------------------------------------------------------------------------------",
        config.BOT_NAME
    )
    asyncio.run(run_bot())
