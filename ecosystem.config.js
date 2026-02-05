module.exports = {
  apps: [
    {
      name: "watch-balance-s1",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: "https://gbg-hll.com:64301",
        RCON_API_TOKEN: "REPLACE_ME",
        DISCORD_BOT_TOKEN: "REPLACE_ME",
        DISCORD_CHANNEL_ID: "REPLACE_ME",
        WATCH_BALANCE_LANG: "2",
        WATCH_BALANCE_INTERVAL_SECS: "300",
        WATCH_BALANCE_MIN_UPDATE_SECS: "600",
        WATCH_BALANCE_BOT_NAME: "CRCON_watch_balance",
        WATCH_BALANCE_DB_PATH: "/data/watch_balance_s1.db",
        BALANCE_WATCH_DATA_PATH: "/data"
      }
    },
    {
      name: "watch-balance-s2",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: "https://gbg-hll.com:64302",
        RCON_API_TOKEN: "REPLACE_ME",
        DISCORD_BOT_TOKEN: "REPLACE_ME",
        DISCORD_CHANNEL_ID: "REPLACE_ME",
        WATCH_BALANCE_LANG: "2",
        WATCH_BALANCE_INTERVAL_SECS: "300",
        WATCH_BALANCE_MIN_UPDATE_SECS: "600",
        WATCH_BALANCE_BOT_NAME: "CRCON_watch_balance",
        WATCH_BALANCE_DB_PATH: "/data/watch_balance_s2.db",
        BALANCE_WATCH_DATA_PATH: "/data"
      }
    },
    {
      name: "watch-balance-s3",
      script: "hll_rcon_tool/custom_tools/watch_balance.py",
      interpreter: "python",
      cron_restart: "30 4 * * *",
      env: {
        RCON_API_BASE_URL: "https://gbg-hll.com:64303",
        RCON_API_TOKEN: "REPLACE_ME",
        DISCORD_BOT_TOKEN: "REPLACE_ME",
        DISCORD_CHANNEL_ID: "REPLACE_ME",
        WATCH_BALANCE_LANG: "2",
        WATCH_BALANCE_INTERVAL_SECS: "300",
        WATCH_BALANCE_MIN_UPDATE_SECS: "600",
        WATCH_BALANCE_BOT_NAME: "CRCON_watch_balance",
        WATCH_BALANCE_DB_PATH: "/data/watch_balance_s3.db",
        BALANCE_WATCH_DATA_PATH: "/data"
      }
    }
  ]
};
