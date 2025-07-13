#!/usr/bin/env python3
"""
Start an A2A Agent Registry Server

This script starts a registry server that agents can register with
for discovery by other agents.
"""

from python_a2a import AgentRegistry, run_registry
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Start an A2A Agent Registry Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=9000, help='Port to bind to (default: 9000)')
    parser.add_argument('--name', default='A2A Registry Server', help='Registry server name')
    parser.add_argument('--description', default='Central registry for agent discovery', help='Registry description')
    
    args = parser.parse_args()
    
    # Create the registry
    registry = AgentRegistry(
        name=args.name,
        description=args.description
    )
    
    print(f"Starting A2A Registry Server on {args.host}:{args.port}")
    print(f"Name: {args.name}")
    print(f"Description: {args.description}")
    print("\nRegistry server is running...")
    print("Agents can register at: http://{}:{}/register".format(args.host, args.port))
    print("Discovery endpoint: http://{}:{}/discover".format(args.host, args.port))
    print("\nPress Ctrl+C to stop")
    
    try:
        # Start the registry server
        run_registry(registry, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down registry server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting registry server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 