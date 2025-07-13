#!/usr/bin/env python3
"""
Start all services for the Agent Networking system

This script starts:
1. Networking API (port 8001)
2. Main Backend API (port 8000) 
3. Agent servers (ports 10003, 10004, 10005)
4. Frontend (port 3000)
"""

import subprocess
import time
import signal
import sys
import os
from typing import List

class ServiceManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        
    def start_service(self, name: str, command: List[str], env: dict = None):
        """Start a service and track the process."""
        print(f"Starting {name}...")
        try:
            process = subprocess.Popen(
                command,
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            print(f"✓ {name} started (PID: {process.pid})")
            return process
        except Exception as e:
            print(f"✗ Failed to start {name}: {e}")
            return None
    
    def start_networking_api(self):
        """Start the networking API service."""
        return self.start_service(
            "Networking API",
            ["python3", "backend/networking_api.py"]
        )
    
    def start_main_backend(self):
        """Start the main backend API."""
        return self.start_service(
            "Main Backend API", 
            ["python3", "backend/main.py"]
        )
    
    def start_agent(self, name: str, agent_file: str, port: int):
        """Start an individual agent."""
        return self.start_service(
            f"{name} Agent",
            ["python3", agent_file]
        )
    
    def start_frontend(self):
        """Start the frontend development server."""
        return self.start_service(
            "Frontend",
            ["npm", "run", "dev"],
            cwd="frontend"
        )
    
    def start_all_services(self):
        """Start all services in the correct order."""
        print("🚀 Starting Agent Networking System...")
        print("=" * 50)
        
        # 1. Start Networking API
        networking_process = self.start_networking_api()
        if not networking_process:
            print("Failed to start Networking API. Exiting.")
            return False
        
        # Wait for networking API to be ready
        print("Waiting for Networking API to be ready...")
        time.sleep(3)
        
        # 2. Start Main Backend
        backend_process = self.start_main_backend()
        if not backend_process:
            print("Failed to start Main Backend. Exiting.")
            return False
        
        # Wait for backend to be ready
        print("Waiting for Main Backend to be ready...")
        time.sleep(3)
        
        # 3. Start Agents
        agents = [
            ("Alice", "agents/alice_agent.py", 10003),
            ("Bob", "agents/bob_agent.py", 10004), 
            ("Charlie", "agents/charlie_agent.py", 10005)
        ]
        
        for name, agent_file, port in agents:
            agent_process = self.start_agent(name, agent_file, port)
            if not agent_process:
                print(f"Failed to start {name} agent. Continuing...")
        
        # Wait for agents to be ready
        print("Waiting for agents to be ready...")
        time.sleep(5)
        
        # 4. Start Frontend (optional)
        try:
            frontend_process = self.start_frontend()
            if frontend_process:
                print("Frontend started successfully")
        except Exception as e:
            print(f"Frontend not started (optional): {e}")
        
        print("\n" + "=" * 50)
        print("🎉 All services started!")
        print("\nServices running:")
        print("• Networking API: http://localhost:8001")
        print("• Main Backend: http://localhost:8000") 
        print("• Alice Agent: http://localhost:10003")
        print("• Bob Agent: http://localhost:10004")
        print("• Charlie Agent: http://localhost:10005")
        print("• Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop all services")
        
        return True
    
    def stop_all_services(self):
        """Stop all running services."""
        print("\n🛑 Stopping all services...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✓ Stopped process {process.pid}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠ Force killed process {process.pid}")
            except Exception as e:
                print(f"✗ Error stopping process {process.pid}: {e}")
        
        self.processes.clear()
        print("All services stopped.")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\nReceived signal {signum}")
        self.stop_all_services()
        sys.exit(0)

def main():
    """Main function to start all services."""
    manager = ServiceManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # Start all services
        if manager.start_all_services():
            # Keep the script running
            while True:
                time.sleep(1)
                # Check if any processes have died
                for process in manager.processes[:]:
                    if process.poll() is not None:
                        print(f"⚠ Process {process.pid} has stopped")
                        manager.processes.remove(process)
        else:
            print("Failed to start services")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt")
        manager.stop_all_services()
    except Exception as e:
        print(f"Error: {e}")
        manager.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main() 