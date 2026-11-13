"""
VrMpc AI Copilot Server (FastAPI Router Bridge)
Allows launching with: uvicorn app.main:app
"""

import sys
import os

# Add parent directory to sys.path to import copilot_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copilot_server import app, VehicleTelemetry, CopilotTacticalOrder, get_copilot_tactics, handle_immediate_alert

__all__ = ["app", "VehicleTelemetry", "CopilotTacticalOrder", "get_copilot_tactics", "handle_immediate_alert"]

