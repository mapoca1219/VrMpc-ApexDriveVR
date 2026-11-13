#!/bin/bash
# Script to launch VrMpc Copilot Server
cd "$(dirname "$0")"

# Check if .env exists, if not load from example
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "=================================================="
echo " Starting VrMpc AI Copilot Server on port ${PORT:-8000}"
echo " Endpoint: http://localhost:${PORT:-8000}/api/v1/copilot/tactics"
echo "=================================================="

python3 -m uvicorn copilot_server:app --host 0.0.0.0 --port ${PORT:-8000} --reload

