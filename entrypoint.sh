#!/bin/bash
echo "Running..."
hypercorn rosterBoardJ.asgi:application -b 0.0.0.0:8080