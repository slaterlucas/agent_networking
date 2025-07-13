#!/usr/bin/env python3
"""
Start All A2A Agents and Run Comprehensive Test

This script starts all user agents simultaneously and then runs the comprehensive test.
"""

import subprocess
import time
import asyncio
import sys
import os
from pathlib import Path

def start_agent(agent_name: str, agent_file: str, port: int):
    """Start an agent in the background."""
    print(f"🚀 Starting {agent_name}'s agent on port {port}...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    agent_path = project_dir / "agents" / agent_file
    
    # Start the agent process
    process = subprocess.Popen(
        [sys.executable, str(agent_path)],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process

def check_agent_health(port: int, timeout: int = 30) -> bool:
    """Check if an agent is healthy by making a request to its endpoint."""
    import httpx
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(f"http://localhost:{port}/.well-known/agent.json", timeout=5.0)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

async def main():
    """Main function to start all agents and run tests."""
    print("🎯 Starting Real A2A Multi-Agent System")
    print("=" * 50)
    
    # Define agents to start
    agents = [
        ("Alice", "alice_agent.py", 10003),
        ("Bob", "bob_agent.py", 10004),
        ("Charlie", "charlie_agent.py", 10005)
    ]
    
    # Start all agents
    processes = []
    for agent_name, agent_file, port in agents:
        process = start_agent(agent_name, agent_file, port)
        processes.append((agent_name, process, port))
    
    # Wait for agents to start
    print("\n⏳ Waiting for agents to start...")
    time.sleep(5)
    
    # Check agent health
    healthy_agents = []
    for agent_name, process, port in processes:
        if check_agent_health(port):
            print(f"✅ {agent_name}'s agent is healthy on port {port}")
            healthy_agents.append(agent_name)
        else:
            print(f"❌ {agent_name}'s agent failed to start on port {port}")
    
    if len(healthy_agents) == 0:
        print("❌ No agents started successfully. Exiting.")
        return
    
    print(f"\n🎉 Successfully started {len(healthy_agents)} agents: {', '.join(healthy_agents)}")
    
    # Run the comprehensive test
    print("\n🧪 Running comprehensive A2A test...")
    test_script = Path(__file__).parent / "test_real_a2a_agents.py"
    
    try:
        # Run the test
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Comprehensive test completed successfully!")
        else:
            print(f"\n❌ Test failed with return code: {result.returncode}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
    
    finally:
        # Clean up: stop all agents
        print("\n🛑 Stopping all agents...")
        for agent_name, process, port in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {agent_name}'s agent")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ Force killed {agent_name}'s agent")
            except Exception as e:
                print(f"❌ Error stopping {agent_name}'s agent: {e}")
        
        print("\n🎯 All agents stopped. Test complete!")

if __name__ == "__main__":
    asyncio.run(main()) 