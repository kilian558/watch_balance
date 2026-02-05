module.exports = {
  apps: [
    {
      name: "watch-balance-s1",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: process.env.PYTHON_INTERPRETER || "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: process.env.RCON_API_BASE_URL_S1,
        RCON_API_TOKEN: process.env.RCON_API_TOKEN,
        RCON_API_TOKEN_HEADER: process.env.RCON_API_TOKEN_HEADER,
        RCON_API_TOKEN_PREFIX: process.env.RCON_API_TOKEN_PREFIX,
        RCON_API_TEAM_ENDPOINT: process.env.RCON_API_TEAM_ENDPOINT,
        RCON_API_PLAYERS_ENDPOINT: process.env.RCON_API_PLAYERS_ENDPOINT,
        RCON_API_TIMEOUT_SECS: process.env.RCON_API_TIMEOUT_SECS,
        DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
        DISCORD_CHANNEL_ID: process.env.DISCORD_CHANNEL_ID_S1,
        WATCH_BALANCE_LANG: process.env.WATCH_BALANCE_LANG,
        WATCH_BALANCE_INTERVAL_SECS: process.env.WATCH_BALANCE_INTERVAL_SECS,
        WATCH_BALANCE_MIN_UPDATE_SECS: process.env.WATCH_BALANCE_MIN_UPDATE_SECS,
        WATCH_BALANCE_BOT_NAME: process.env.WATCH_BALANCE_BOT_NAME,
        WATCH_BALANCE_DB_PATH: process.env.WATCH_BALANCE_DB_PATH_S1,
        BALANCE_WATCH_DATA_PATH: process.env.BALANCE_WATCH_DATA_PATH
      }
    },
    {
      name: "watch-balance-s2",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: process.env.PYTHON_INTERPRETER || "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: process.env.RCON_API_BASE_URL_S2,
        RCON_API_TOKEN: process.env.RCON_API_TOKEN,
        RCON_API_TOKEN_HEADER: process.env.RCON_API_TOKEN_HEADER,
        RCON_API_TOKEN_PREFIX: process.env.RCON_API_TOKEN_PREFIX,
        RCON_API_TEAM_ENDPOINT: process.env.RCON_API_TEAM_ENDPOINT,
        RCON_API_PLAYERS_ENDPOINT: process.env.RCON_API_PLAYERS_ENDPOINT,
        RCON_API_TIMEOUT_SECS: process.env.RCON_API_TIMEOUT_SECS,
        DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
        DISCORD_CHANNEL_ID: process.env.DISCORD_CHANNEL_ID_S2,
        WATCH_BALANCE_LANG: process.env.WATCH_BALANCE_LANG,
        WATCH_BALANCE_INTERVAL_SECS: process.env.WATCH_BALANCE_INTERVAL_SECS,
        WATCH_BALANCE_MIN_UPDATE_SECS: process.env.WATCH_BALANCE_MIN_UPDATE_SECS,
        WATCH_BALANCE_BOT_NAME: process.env.WATCH_BALANCE_BOT_NAME,
        WATCH_BALANCE_DB_PATH: process.env.WATCH_BALANCE_DB_PATH_S2,
        BALANCE_WATCH_DATA_PATH: process.env.BALANCE_WATCH_DATA_PATH
      }
    },
    {
      name: "watch-balance-s3",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: process.env.PYTHON_INTERPRETER || "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: process.env.RCON_API_BASE_URL_S3,
        RCON_API_TOKEN: process.env.RCON_API_TOKEN,
        RCON_API_TOKEN_HEADER: process.env.RCON_API_TOKEN_HEADER,
        RCON_API_TOKEN_PREFIX: process.env.RCON_API_TOKEN_PREFIX,
        RCON_API_TEAM_ENDPOINT: process.env.RCON_API_TEAM_ENDPOINT,
        RCON_API_PLAYERS_ENDPOINT: process.env.RCON_API_PLAYERS_ENDPOINT,
        RCON_API_TIMEOUT_SECS: process.env.RCON_API_TIMEOUT_SECS,
        DISCORD_BOT_TOKEN: process.env.DISCORD_BOT_TOKEN,
        DISCORD_CHANNEL_ID: process.env.DISCORD_CHANNEL_ID_S3,
        WATCH_BALANCE_LANG: process.env.WATCH_BALANCE_LANG,
        WATCH_BALANCE_INTERVAL_SECS: process.env.WATCH_BALANCE_INTERVAL_SECS,
        WATCH_BALANCE_MIN_UPDATE_SECS: process.env.WATCH_BALANCE_MIN_UPDATE_SECS,
        WATCH_BALANCE_BOT_NAME: process.env.WATCH_BALANCE_BOT_NAME,
        WATCH_BALANCE_DB_PATH: process.env.WATCH_BALANCE_DB_PATH_S3,
        BALANCE_WATCH_DATA_PATH: process.env.BALANCE_WATCH_DATA_PATH
      }
    }
  ]
};
