#!/usr/bin/env python3
"""
Start All A2A Agents and Run Comprehensive Test

This script starts all user agents simultaneously and then runs the comprehensive test.
"""

import subprocess
import time

AGENTS = [
    ("Alice", "agents.alice_agent:app", 10003),
    ("Bob", "agents.bob_agent:app", 10004),
    ("Charlie", "agents.charlie_agent:app", 10005),
]

processes = []

for name, app_path, port in AGENTS:
    print(f"Starting {name} agent on port {port}...")
    p = subprocess.Popen([
        "uvicorn", app_path, "--host", "0.0.0.0", "--port", str(port), "--reload"
    ])
    processes.append(p)
    time.sleep(1)

print("All agents started. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping agents...")
    for p in processes:
        p.terminate()
    print("All agents stopped.") 