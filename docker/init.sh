#!/bin/bash

set -e  # Exit immediately on error

BENCH_DIR="/home/frappe/frappe-bench"

# If bench already exists
if [ -d "$BENCH_DIR/sites" ]; then
    echo "Bench already exists, skipping init"
    cd "$BENCH_DIR"
    bench start
    exit 0
fi

echo "Creating new bench..."

export PATH="${NVM_DIR}/versions/node/v${NODE_VERSION_DEVELOP}/bin/:${PATH}"

# Step 1: Init bench
bench init --skip-redis-config-generation frappe-bench

# Step 2: Move into bench dir — this is **critical**
cd "$BENCH_DIR"

# Step 3: Set config (only safe AFTER cd)
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Step 4: Clean up Procfile
sed -i '/redis/d' Procfile || true
sed -i '/watch/d' Procfile || true

# Step 5: Get ERPNext app
bench get-app erpnext https://github.com/Yamini0527/ERPNext

# Step 6: Create site
bench new-site erpnext.localhost \
  --force \
  --mariadb-root-password 123 \
  --admin-password admin \
  --no-mariadb-socket

# Step 7: Install and configure app
bench --site erpnext.localhost install-app erpnext
bench --site erpnext.localhost set-config developer_mode 1
bench --site erpnext.localhost migrate
bench --site erpnext.localhost clear-cache

# Step 8: Start the bench
bench start

