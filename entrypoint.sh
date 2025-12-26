#!/bin/bash
set -e

# Wait for DB if necessary (optional, but good for stability)
# You can add a wait-for-it script here if needed

if [ "$APP_ENV" = "production" ]; then
    echo "------------------------------------------------"
    echo " Launching in PRODUCTION mode"
    echo "------------------------------------------------"
    # Raspberry Pi 1GBメモリ想定でデフォルトワーカー数を 1 に設定
    # --timeout 600: PyTorch/YOLO ロードに時間がかかるため延長
    WORKERS=${GUNICORN_WORKERS:-1}
    TIMEOUT=${GUNICORN_TIMEOUT:-600}
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers $WORKERS \
        --timeout $TIMEOUT \
        --access-logfile - \
        --error-logfile -
else
    echo "------------------------------------------------"
    echo " Launching in DEVELOPMENT mode"
    echo "------------------------------------------------"
    # データベースマイグレーションを適用
    echo "Applying database migrations..."
    python manage.py migrate --noinput
    
    # Start Tailwind CSS watcher in the background
    npm run watch &
    
    # Start Django development server
    exec python manage.py runserver 0.0.0.0:8000
fi
