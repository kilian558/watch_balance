#!/bin/bash
# Reload PM2 processes after configuration changes

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Export all variables from .env
set -a
source .env
set +a

# Reload PM2
pm2 reload ecosystem.config.js
