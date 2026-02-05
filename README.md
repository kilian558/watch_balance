# watch_balance

Discord bot that monitors team balance on Hell Let Loose servers using the CRCON HTTP API.
It posts a single embed per channel and edits it on updates to avoid spam.

## Requirements
- Python 3.9+
- CRCON API reachable for each server
- Discord bot token and channel IDs
- PM2 (optional, for process management and scheduled restarts)

## Setup
1) Install dependencies used by your CRCON environment.
2) Copy `.env.example` to `.env`: `cp .env.example .env`
3) Edit `.env` and configure your Discord bot token, RCON API credentials, and server URLs.
4) Make the start script executable: `chmod +x start.sh reload.sh`
5) Start with PM2 using the provided script.

## PM2 (recommended)
The `.env` file contains your configuration. PM2 requires environment variables to be loaded before starting.

Start:
```bash
./start.sh
```

Reload after changes:
```bash
./reload.sh
```

Stop:
```bash
pm2 stop ecosystem.config.js
```

## Environment variables
Per server:
- `RCON_API_BASE_URL` (example: `https://gbg-hll.com:64301`)
- `RCON_API_TOKEN`
- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`

Optional:
- `RCON_API_TOKEN_HEADER` (default: `Authorization`)
- `RCON_API_TOKEN_PREFIX` (default: `Bearer`)
- `RCON_API_TEAM_ENDPOINT` (default: `get_team_view`)
- `RCON_API_PLAYERS_ENDPOINT` (default: `get_detailed_players`)
- `RCON_API_TIMEOUT_SECS` (default: `15`)
- `WATCH_BALANCE_INTERVAL_SECS` (default: `300`)
- `WATCH_BALANCE_MIN_UPDATE_SECS` (default: `300`)
- `WATCH_BALANCE_DB_PATH` (per server, to keep a single message across restarts)

## Notes
- If `RCON_API_BASE_URL` or `DISCORD_CHANNEL_ID` is empty for a server, that process will skip updates and continue running.
- The PM2 config includes a daily restart at 04:30. The bot reuses the same message ID from its DB, so you still have only one message in the channel.
