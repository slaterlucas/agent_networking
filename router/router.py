"""
LLM-Powered Router System

This router system can understand plain English requirements and automatically
generate and execute the necessary commands to establish communication between agents.
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import signal
import time
from dataclasses import dataclass
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessInfo:
    """Information about a running process"""
    name: str
    process: subprocess.Popen
    command: str
    port: Optional[int] = None
    started_at: datetime = None

class LLMRouter:
    """LLM-powered router for agent communication setup"""
    
    def __init__(self, use_llm: bool = True):
        self.running_processes: Dict[str, ProcessInfo] = {}
        self.use_llm = use_llm
        self.base_commands = {
            "registry": "uv run python -m python_a2a.registry --host 0.0.0.0 --port 9000",
            "restaurant_selector": "uv run uvicorn adk.restaurant_selector.A2A:app --host 0.0.0.0 --port 8080 --reload",
            "alice_agent": "uv run python -m agents.personal_agent --name Alice --port 10001",
            "bob_agent": "uv run python -m agents.personal_agent --name Bob --port 10002"
        }
        
        # Initialize OpenAI client if using LLM
        if self.use_llm:
            self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("Initialized OpenAI client")
        else:
            logger.warning("OPENAI_API_KEY not found, falling back to pattern matching")
            self.use_llm = False
    
    def parse_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Parse plain English requirements using LLM or fallback to pattern matching.
        """
        if self.use_llm:
            return self._parse_with_llm(requirements)
        else:
            return self._parse_with_pattern_matching(requirements)
    
    def _parse_with_llm(self, requirements: str) -> Dict[str, Any]:
        """Parse requirements using OpenAI LLM"""
        try:
            system_prompt = """You are a system that parses plain English requirements for setting up agent communication. 

Given a user requirement, extract:
1. agents_needed: List of agent names mentioned (alice, bob, charlie, diana)
2. services_needed: List of services needed (always include 'registry', add 'restaurant_selector' if food/dining/restaurant related)
3. test_scenario: 'restaurant_recommendation' if testing/recommendation is mentioned, otherwise null

Return ONLY a valid JSON object with these exact keys. No explanations.

Examples:
Input: "Alice needs to talk to Bob for restaurant recommendations"
Output: {"agents_needed": ["alice", "bob"], "services_needed": ["registry", "restaurant_selector"], "test_scenario": "restaurant_recommendation"}

Input: "Alice needs help"
Output: {"agents_needed": ["alice"], "services_needed": ["registry"], "test_scenario": null}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using more cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": requirements}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate result structure
            if not all(key in result for key in ["agents_needed", "services_needed", "test_scenario"]):
                raise ValueError("Invalid LLM response structure")
            
            logger.info(f"OpenAI parsed requirements: {result}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}, falling back to pattern matching")
            return self._parse_with_pattern_matching(requirements)
    
    def _parse_with_pattern_matching(self, requirements: str) -> Dict[str, Any]:
        """Fallback pattern matching parser"""
        logger.info("Using pattern matching parser")
        requirements = requirements.lower()
        
        parsed = {
            "agents_needed": [],
            "services_needed": [],
            "test_scenario": None
        }
        
        # Check for agents mentioned
        agents = ["alice", "bob", "charlie", "diana"]
        for agent in agents:
            if agent in requirements:
                parsed["agents_needed"].append(agent)
        
        # Check for services needed
        if "restaurant" in requirements or "food" in requirements or "dining" in requirements:
            parsed["services_needed"].append("restaurant_selector")
        
        # Always need registry for agent communication
        parsed["services_needed"].append("registry")
        
        # Check for test scenarios
        if "test" in requirements or "recommend" in requirements:
            parsed["test_scenario"] = "restaurant_recommendation"
        
        return parsed
    
    def generate_commands(self, parsed_requirements: Dict[str, Any]) -> List[str]:
        """
        Generate the commands needed based on parsed requirements.
        In a real implementation, this would use an LLM to generate commands.
        """
        commands = []
        
        # Always start with registry
        if "registry" in parsed_requirements["services_needed"]:
            commands.append(self.base_commands["registry"])
        
        # Add restaurant selector if needed
        if "restaurant_selector" in parsed_requirements["services_needed"]:
            commands.append(self.base_commands["restaurant_selector"])
        
        # Add agents
        for agent in parsed_requirements["agents_needed"]:
            if f"{agent}_agent" in self.base_commands:
                commands.append(self.base_commands[f"{agent}_agent"])
        
        return commands
    
    def generate_test_commands(self, parsed_requirements: Dict[str, Any]) -> List[str]:
        """Generate test commands based on the scenario"""
        test_commands = []
        
        if parsed_requirements["test_scenario"] == "restaurant_recommendation":
            # Test the full chain with Alice's agent
            test_commands.append('''curl -X POST http://localhost:10001/invoke -H "Content-Type: application/json" -d '{"skill": "restaurant_recommendation", "input": {"location": "North Beach, San Francisco", "cuisines": ["japanese"], "diet": ["pescatarian"], "time_window": ["2025-07-15T18:00", "2025-07-15T21:00"], "budget": "high"}}'
            ''')
        
        return test_commands
    
    async def start_process(self, name: str, command: str, wait_time: int = 2) -> bool:
        """Start a process and track it"""
        try:
            logger.info(f"Starting {name}: {command}")
            
            # Start the process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process info
            self.running_processes[name] = ProcessInfo(
                name=name,
                process=process,
                command=command,
                started_at=datetime.now()
            )
            
            # Wait a bit for the process to start
            await asyncio.sleep(wait_time)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {name} started successfully")
                return True
            else:
                logger.error(f"❌ {name} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {name}: {e}")
            return False
    
    def stop_all_processes(self):
        """Stop all running processes"""
        logger.info("Stopping all processes...")
        
        for name, proc_info in self.running_processes.items():
            try:
                if proc_info.process.poll() is None:
                    proc_info.process.terminate()
                    # Wait for graceful shutdown
                    proc_info.process.wait(timeout=5)
                    logger.info(f"✅ Stopped {name}")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                proc_info.process.kill()
                logger.info(f"🔪 Force killed {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self.running_processes.clear()
    
    async def execute_test_commands(self, test_commands: List[str]):
        """Execute test commands"""
        logger.info("Executing test commands...")
        
        for i, command in enumerate(test_commands):
            logger.info(f"Running test {i+1}: {command.strip()}")
            
            try:
                # Run the command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Test {i+1} passed")
                    logger.info(f"Output: {result.stdout}")
                else:
                    logger.error(f"❌ Test {i+1} failed")
                    logger.error(f"Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Test {i+1} timed out")
            except Exception as e:
                logger.error(f"❌ Test {i+1} error: {e}")
    
    async def setup_communication(self, requirements: str) -> bool:
        """
        Main method to set up communication based on plain English requirements
        """
        logger.info("🚀 Setting up agent communication...")
        logger.info(f"Requirements: {requirements}")
        
        # Parse requirements
        parsed = self.parse_requirements(requirements)
        logger.info(f"Parsed requirements: {parsed}")
        
        # Generate commands
        commands = self.generate_commands(parsed)
        logger.info(f"Generated commands: {commands}")
        
        # Start processes in order
        success = True
        for i, command in enumerate(commands):
            process_name = f"service_{i}"
            if "registry" in command:
                process_name = "registry"
            elif "restaurant_selector" in command:
                process_name = "restaurant_selector"
            elif "Alice" in command:
                process_name = "alice_agent"
            elif "Bob" in command:
                process_name = "bob_agent"
            
            # Start process with appropriate wait time
            wait_time = 3 if "registry" in command else 2
            if not await self.start_process(process_name, command, wait_time):
                success = False
                break
        
        if success:
            logger.info("✅ All services started successfully!")
            
            # Generate and execute test commands
            test_commands = self.generate_test_commands(parsed)
            if test_commands:
                logger.info("Running tests...")
                await asyncio.sleep(2)  # Wait for services to be ready
                await self.execute_test_commands(test_commands)
            
            return True
        else:
            logger.error("❌ Failed to start some services")
            self.stop_all_processes()
            return False
    
    def status(self) -> Dict[str, Any]:
        """Get status of all running processes"""
        status = {
            "total_processes": len(self.running_processes),
            "processes": {}
        }
        
        for name, proc_info in self.running_processes.items():
            is_running = proc_info.process.poll() is None
            status["processes"][name] = {
                "name": name,
                "running": is_running,
                "command": proc_info.command,
                "started_at": proc_info.started_at.isoformat() if proc_info.started_at else None
            }
        
        return status

async def main():
    """Main entry point"""
    router = LLMRouter()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        router.stop_all_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Example usage
        if len(sys.argv) > 1:
            requirements = " ".join(sys.argv[1:])
        else:
            requirements = "Alice needs to talk to Bob for restaurant recommendations"
        
        logger.info(f"🎯 Processing requirements: {requirements}")
        
        # Setup communication
        success = await router.setup_communication(requirements)
        
        if success:
            logger.info("🎉 Communication setup complete!")
            logger.info("Services are running. Press Ctrl+C to stop all services.")
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        else:
            logger.error("❌ Failed to setup communication")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        router.stop_all_processes()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        router.stop_all_processes()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
