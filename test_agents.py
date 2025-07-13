#!/usr/bin/env python3
"""
Test All A2A Agents

This script tests all user agents to ensure they're working correctly.
"""

import requests
import time
import json

AGENTS = [
    ("Alice", "http://localhost:10003"),
    ("Bob", "http://localhost:10004"),
    ("Charlie", "http://localhost:10005"),
]

def test_agent(name, base_url):
    """Test a single agent's /a2a/execute endpoint"""
    try:
        response = requests.post(
            f"{base_url}/a2a/execute",
            json={"message": {"content": f"Hello {name}!", "sender": "test"}},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {name}: Success - {result.get('status', {}).get('state', 'unknown')}")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection error - {e}")
        return False

def main():
    print("Testing all A2A agents...")
    print("=" * 50)
    
    results = []
    for name, base_url in AGENTS:
        results.append(test_agent(name, base_url))
        time.sleep(1)  # Small delay between tests
    
    print("=" * 50)
    success_count = sum(results)
    total_count = len(AGENTS)
    
    if success_count == total_count:
        print(f"🎉 All {total_count} agents are working correctly!")
    else:
        print(f"⚠️  {success_count}/{total_count} agents are working")
        print("Make sure all agents are running with: python3 start_all_agents.py")

if __name__ == "__main__":
    main() 