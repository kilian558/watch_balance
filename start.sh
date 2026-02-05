#!/bin/bash
# Load environment variables from .env file and start PM2

if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Export all variables from .env
set -a
source .env
set +a

# Start PM2
pm2 start ecosystem.config.js
