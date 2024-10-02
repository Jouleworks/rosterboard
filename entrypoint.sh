#!/bin/bash
if [ ! -f ./config/settings.ini ]; then
  echo "Could not find the config file, assuming this is a new installation and launching the setup server."

  cd setup/ui
  npm run integrate
  cd ../../

  hypercorn setup.app:asgi_app -b 0.0.0.0:8080
else
  echo "Running..."
  hypercorn rosterBoardJ.asgi:application -b 0.0.0.0:8080
fi
