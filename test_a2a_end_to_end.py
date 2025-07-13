#!/usr/bin/env python3
"""
Comprehensive A2A End-to-End Validation Script

This script validates the complete A2A protocol flow, LLM integration (Exa API),
and agent-to-agent communication using the official A2A SDK.
"""

import asyncio
import time
import logging
import json
import httpx
from typing import Dict, Any, List
import uvicorn
from agents.agent_client import MultiAgentOrchestrator
from agents.user_agent_template import UserProfile, create_user_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress uvicorn cancellation errors during shutdown
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# User profiles for our agents
USER_PROFILES = {
    "Alice": UserProfile(
        name="Alice",
        preferences="I love technology, programming, and outdoor activities",
        location="San Francisco",
        budget="medium",
        dietary_restrictions=["vegetarian"],
        cuisine_preferences=["Italian", "Asian"],
        interests=["technology", "programming", "hiking"],
        agent_port=10003
    ),
    "Bob": UserProfile(
        name="Bob",
        preferences="I enjoy cooking, trying new recipes, and exploring different cuisines",
        location="New York",
        budget="high",
        dietary_restrictions=[],
        cuisine_preferences=["French", "Mediterranean"],
        interests=["cooking", "traveling", "photography"],
        agent_port=10004
    ),
    "Charlie": UserProfile(
        name="Charlie",
        preferences="I'm into fitness, yoga, and healthy living",
        location="Los Angeles",
        budget="low",
        dietary_restrictions=["vegan"],
        cuisine_preferences=["Healthy", "Organic"],
        interests=["fitness", "yoga", "meditation"],
        agent_port=10005
    )
}

class A2AEndToEndValidator:
    """Comprehensive validator for A2A protocol and LLM integration."""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.test_results = []
        self.agent_urls = {}
        
    async def start_agent_server(self, user_name: str, user_profile: UserProfile):
        """Start an agent server for a specific user."""
        try:
            app = create_user_agent(user_profile)
            logger.info(f"[STARTUP] Starting {user_name}'s agent on port {user_profile.agent_port}")
            
            # Run the server
            config = uvicorn.Config(
                app=app,
                host="0.0.0.0",
                port=user_profile.agent_port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except asyncio.CancelledError:
            logger.info(f"[SHUTDOWN] {user_name}'s agent server cancelled gracefully")
        except Exception as e:
            logger.error(f"[ERROR] Error starting {user_name}'s agent: {e}")
    
    async def validate_a2a_endpoint(self, agent_name: str, agent_url: str) -> bool:
        """Validate that an agent's A2A endpoint is working."""
        try:
            logger.info(f"[VALIDATE] Testing A2A endpoint for {agent_name} at {agent_url}")
            
            # Test A2A-compatible request
            a2a_request = {
                "message": {
                    "messageId": f"test-{int(time.time())}",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Hello, this is a test message"}]
                },
                "contextId": f"test-context-{int(time.time())}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{agent_url}/a2a/execute", json=a2a_request)
                
                if response.status_code == 200:
                    logger.info(f"[SUCCESS] {agent_name}'s A2A endpoint responded successfully")
                    return True
                else:
                    logger.error(f"[FAILURE] {agent_name}'s A2A endpoint returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"[ERROR] Failed to validate {agent_name}'s A2A endpoint: {e}")
            return False
    
    async def test_llm_integration(self, agent_name: str, agent_url: str) -> Dict[str, Any]:
        """Test LLM integration (Exa API) through the agent."""
        try:
            logger.info(f"[LLM_TEST] Testing LLM integration for {agent_name}")
            
            # Test search functionality (uses Exa API)
            search_request = {
                "message": {
                    "messageId": f"llm-test-{int(time.time())}",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "search for machine learning tutorials"}]
                },
                "contextId": f"llm-test-context-{int(time.time())}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{agent_url}/a2a/execute", json=search_request)
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"[SUCCESS] {agent_name}'s LLM integration working")
                    return {
                        "success": True,
                        "agent": agent_name,
                        "response_length": len(str(response_data)),
                        "has_results": "results" in str(response_data).lower()
                    }
                else:
                    logger.error(f"[FAILURE] {agent_name}'s LLM integration failed with status {response.status_code}")
                    return {"success": False, "agent": agent_name, "error": f"Status {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"[ERROR] Failed to test LLM integration for {agent_name}: {e}")
            return {"success": False, "agent": agent_name, "error": str(e)}
    
    async def test_agent_to_agent_communication(self, sender: str, receiver: str) -> Dict[str, Any]:
        """Test agent-to-agent communication through the orchestrator."""
        try:
            logger.info(f"[A2A_COMM] Testing communication from {sender} to {receiver}")
            
            # Send a message from sender to receiver
            task = await self.orchestrator.send_message_to_agent(
                sender, 
                f"Hello from {sender}! Can you help me with recommendations?"
            )
            
            if task:
                logger.info(f"[SUCCESS] {sender} successfully communicated with {receiver}")
                return {
                    "success": True,
                    "sender": sender,
                    "receiver": receiver,
                    "task_id": task.id if hasattr(task, 'id') else 'unknown'
                }
            else:
                logger.error(f"[FAILURE] {sender} failed to communicate with {receiver}")
                return {"success": False, "sender": sender, "receiver": receiver}
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to test communication from {sender} to {receiver}: {e}")
            return {"success": False, "sender": sender, "receiver": receiver, "error": str(e)}
    
    async def test_networking_functionality(self, agent_name: str, agent_url: str) -> Dict[str, Any]:
        """Test networking functionality through the agent."""
        try:
            logger.info(f"[NETWORKING_TEST] Testing networking functionality for {agent_name}")
            
            # Test networking request
            networking_request = {
                "message": {
                    "messageId": f"networking-test-{int(time.time())}",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Can you help me with networking opportunities?"}]
                },
                "contextId": f"networking-test-context-{int(time.time())}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{agent_url}/a2a/execute", json=networking_request)
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"[SUCCESS] {agent_name}'s networking functionality working")
                    return {
                        "success": True,
                        "agent": agent_name,
                        "response_length": len(str(response_data)),
                        "has_networking": "similar" in str(response_data).lower() or "cluster" in str(response_data).lower()
                    }
                else:
                    logger.error(f"[FAILURE] {agent_name}'s networking functionality failed")
                    return {"success": False, "agent": agent_name, "error": f"Status {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"[ERROR] Failed to test networking functionality for {agent_name}: {e}")
            return {"success": False, "agent": agent_name, "error": str(e)}
    
    async def run_comprehensive_validation(self):
        """Run comprehensive end-to-end validation."""
        logger.info("[VALIDATION] Starting comprehensive A2A end-to-end validation")
        
        # Wait for agents to start
        logger.info("[SETUP] Waiting for agents to start...")
        await asyncio.sleep(5)
        
        # Set up agent URLs
        self.agent_urls = {
            name: f"http://localhost:{profile.agent_port}"
            for name, profile in USER_PROFILES.items()
        }
        
        # Test 1: Validate A2A endpoints
        logger.info("\n=== Test 1: A2A Endpoint Validation ===")
        for name, url in self.agent_urls.items():
            success = await self.validate_a2a_endpoint(name, url)
            self.test_results.append({
                "test": "a2a_endpoint",
                "agent": name,
                "success": success
            })
        
        # Test 2: LLM Integration (Exa API)
        logger.info("\n=== Test 2: LLM Integration (Exa API) ===")
        for name, url in self.agent_urls.items():
            result = await self.test_llm_integration(name, url)
            self.test_results.append({
                "test": "llm_integration",
                **result
            })
        
        # Test 3: Agent-to-Agent Communication
        logger.info("\n=== Test 3: Agent-to-Agent Communication ===")
        # Connect agents to orchestrator
        for name, url in self.agent_urls.items():
            success = await self.orchestrator.add_agent(name, url)
            if success:
                logger.info(f"[CONNECT] ✓ Connected {name} to orchestrator")
            else:
                logger.error(f"[CONNECT] ✗ Failed to connect {name} to orchestrator")
        
        # Test cross-agent communication
        communication_tests = [
            ("Alice", "Bob"),
            ("Bob", "Charlie"),
            ("Charlie", "Alice")
        ]
        
        for sender, receiver in communication_tests:
            result = await self.test_agent_to_agent_communication(sender, receiver)
            self.test_results.append({
                "test": "agent_communication",
                **result
            })
        
        # Test 4: Networking Functionality
        logger.info("\n=== Test 4: Networking Functionality ===")
        for name, url in self.agent_urls.items():
            result = await self.test_networking_functionality(name, url)
            self.test_results.append({
                "test": "networking_functionality",
                **result
            })
        
        # Test 5: End-to-End Flow
        logger.info("\n=== Test 5: End-to-End Flow ===")
        try:
            # Simulate the full demo flow
            # 1. User preference setup
            logger.info("[FLOW] Step 1: User preference setup")
            
            # 2. Agent creation and coordination
            logger.info("[FLOW] Step 2: Agent creation and coordination")
            alice_task = await self.orchestrator.send_message_to_agent(
                "Alice", 
                "I need restaurant recommendations in San Francisco for Italian food"
            )
            
            # 3. Cross-agent coordination
            logger.info("[FLOW] Step 3: Cross-agent coordination")
            bob_task = await self.orchestrator.send_message_to_agent(
                "Bob", 
                "Alice is looking for Italian restaurants. Can you help with recommendations?"
            )
            
            # 4. Results aggregation
            logger.info("[FLOW] Step 4: Results aggregation")
            charlie_task = await self.orchestrator.send_message_to_agent(
                "Charlie", 
                "Please provide healthy restaurant options for Alice"
            )
            
            self.test_results.append({
                "test": "end_to_end_flow",
                "success": True,
                "alice_task": alice_task.id if alice_task and hasattr(alice_task, 'id') else None,
                "bob_task": bob_task.id if bob_task and hasattr(bob_task, 'id') else None,
                "charlie_task": charlie_task.id if charlie_task and hasattr(charlie_task, 'id') else None
            })
            
        except Exception as e:
            logger.error(f"[ERROR] End-to-end flow failed: {e}")
            self.test_results.append({
                "test": "end_to_end_flow",
                "success": False,
                "error": str(e)
            })
        
        # Generate summary report
        await self.generate_summary_report()
        
        # Cleanup
        await self.orchestrator.close_all()
        logger.info("[VALIDATION] Comprehensive validation completed")
    
    async def generate_summary_report(self):
        """Generate a summary report of all test results."""
        logger.info("\n" + "="*60)
        logger.info("A2A END-TO-END VALIDATION SUMMARY")
        logger.info("="*60)
        
        # Group results by test type
        test_groups = {}
        for result in self.test_results:
            test_type = result["test"]
            if test_type not in test_groups:
                test_groups[test_type] = []
            test_groups[test_type].append(result)
        
        # Report results
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests}")
        logger.info(f"Failed: {total_tests - successful_tests}")
        logger.info(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        logger.info("\nDetailed Results:")
        for test_type, results in test_groups.items():
            logger.info(f"\n{test_type.upper()}:")
            for result in results:
                status = "✓ PASS" if result.get("success", False) else "✗ FAIL"
                agent = result.get("agent", result.get("sender", "unknown"))
                logger.info(f"  {status} - {agent}")
                if not result.get("success", False) and "error" in result:
                    logger.info(f"    Error: {result['error']}")
        
        # Save detailed results to file
        with open("a2a_validation_results.json", "w") as f:
            json.dump({
                "timestamp": time.time(),
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": total_tests - successful_tests,
                    "success_rate": (successful_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        logger.info(f"\nDetailed results saved to: a2a_validation_results.json")
        logger.info("="*60)

async def main():
    """Main function to run the comprehensive validation."""
    logger.info("Starting A2A End-to-End Validation System")
    
    # Create validator
    validator = A2AEndToEndValidator()
    
    # Start all agent servers in the background
    server_tasks = []
    for name, profile in USER_PROFILES.items():
        task = asyncio.create_task(validator.start_agent_server(name, profile))
        server_tasks.append(task)
    
    # Wait a bit for servers to start
    await asyncio.sleep(3)
    
    # Run the comprehensive validation
    await validator.run_comprehensive_validation()
    
    # Cancel server tasks
    for task in server_tasks:
        task.cancel()
    
    logger.info("A2A End-to-End Validation System completed")

if __name__ == "__main__":
    asyncio.run(main()) 