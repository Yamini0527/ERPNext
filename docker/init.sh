#!/bin/bash

# Check if bench already exists
if [ -d "/home/frappe/frappe-bench/sites" ]; then
    echo "Bench already exists, skipping init"
    cd /home/frappe/frappe-bench
    bench start
    exit 0
else
    echo "Creating new bench..."
fi

# Add Node.js to PATH
export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"

# Initialize bench
bench init --skip-redis-config-generation frappe-bench

cd frappe-bench

# Set container-based DB & Redis hosts
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Optional cleanup in Procfile
sed -i '/redis/d' ./Procfile || true
sed -i '/watch/d' ./Procfile || true

# Pull custom ERPNext app
bench get-app erpnext https://github.com/Yamini0527/ERPNext

# Create site and install app
bench new-site erpnext.localhost \
  --force \
  --mariadb-root-password 123 \
  --admin-password admin \
  --no-mariadb-socket

bench --site erpnext.localhost install-app erpnext
bench --site erpnext.localhost set-config developer_mode 1
bench --site erpnext.localhost migrate
bench --site erpnext.localhost clear-cache
bench use erpnext.localhost

# Start bench
bench start

