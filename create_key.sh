mkdir -p ./data/logs
echo "APP_SECRET_KEY=$(openssl rand -hex 32)" >> .env
