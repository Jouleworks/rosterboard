#!/bin/bash
echo "ROSTERBOARD is warming up..."
if [ ! -f ./config/settings.ini ]; then
  echo "Could not find the config file, assuming this is a new installation and launching the setup server."
  hypercorn setup.app:asgi_app -b 0.0.0.0:9418
else
  echo "Running..."
  python manage.py migrate
  python manage.py collectstatic --no-input
  hypercorn rosterBoardJ.asgi:application -b 0.0.0.0:9418
fi
