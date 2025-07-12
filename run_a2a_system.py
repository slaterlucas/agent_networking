#!/usr/bin/env python3
"""
A2A Agent Networking System Runner

Simple script to demonstrate the complete A2A integration with your existing
people networking system.
"""

import asyncio
import os
import json
from dotenv import load_dotenv
from adk.a2a_main import A2ANetworkingSystem
from adk.monitoring import monitor, CollaborationTracker
from networking.networking import demo_example

# Load environment variables
load_dotenv()

async def run_a2a_demo():
    """Run a comprehensive A2A system demonstration."""
    print("🚀 Starting A2A Agent Networking System Demo")
    print("=" * 50)
    
    # Initialize the system
    system = A2ANetworkingSystem()
    
    try:
        # Step 1: Initialize with extended sample data
        print("\n📊 Step 1: Initializing System with User Preferences")
        sample_data = {
            "alice": "I love Italian food, especially vegetarian options. I enjoy quiet restaurants for business meetings and prefer places under $30. I'm health-conscious and avoid spicy food.",
            "bob": "I'm a big fan of sushi and Japanese cuisine. I like trendy places with good atmosphere and don't mind spending up to $50. I enjoy trying new restaurants and love seafood.",
            "charlie": "I prefer healthy food, salads, and Mediterranean cuisine. I'm vegetarian and like casual dining experiences. I enjoy outdoor seating when available.",
            "diana": "I love trying new cuisines, especially Thai and Vietnamese. I prefer authentic places with good reviews and don't mind traveling for good food.",
            "eve": "I enjoy comfort food, American cuisine, and family-friendly restaurants. Budget-conscious, prefer under $25. I have two kids so need kid-friendly places.",
            "frank": "I'm into fine dining, French cuisine, and wine pairings. I appreciate excellent service and ambiance. Price is not a concern for special occasions.",
            "grace": "I love Mexican food, especially authentic tacos and fresh ingredients. I prefer casual, lively atmospheres and enjoy spicy food.",
            "henry": "I'm a foodie who loves experimenting with fusion cuisine. I enjoy innovative restaurants with creative menus and unique dining experiences.",
            "ivy": "I prefer Asian cuisine, especially Korean and Chinese food. I like spicy food and informal dining settings. I'm always looking for authentic hole-in-the-wall places.",
            "jack": "I'm a meat lover who enjoys BBQ and steakhouses. I prefer hearty meals and don't mind spending for good quality. I enjoy sports bars and casual dining."
        }
        
        await system.initialize(sample_data)
        print(f"✅ System initialized with {len(sample_data)} users")
        
        # Step 2: Run system health check
        print("\n🔍 Step 2: Running System Health Check")
        test_results = await system.test_system()
        
        print("System Health Check Results:")
        for component, result in test_results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"  {component}: {status}")
            if not result.get("success", False):
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        # Step 3: Demonstrate people clustering and networking
        print("\n👥 Step 3: Demonstrating People Clustering")
        status = await system.get_system_status()
        networking_stats = status.get("networking_stats", {})
        print(f"Total People: {networking_stats.get('total_people', 0)}")
        print(f"Clusters Created: {networking_stats.get('clusters_created', 0)}")
        
        # Step 4: Demonstrate individual user analysis
        print("\n🎯 Step 4: Individual User Analysis")
        user_to_analyze = "alice"
        
        # This would be done through A2A protocol in production
        print(f"Analyzing preferences for user: {user_to_analyze}")
        
        # Step 5: Demonstrate collaborative restaurant finding
        print("\n🤝 Step 5: Collaborative Restaurant Finding")
        
        collaboration_scenarios = [
            {
                "users": ["alice", "bob"],
                "task": "Find restaurant for business lunch",
                "description": "Vegetarian-friendly meets sushi lover"
            },
            {
                "users": ["charlie", "diana", "grace"],
                "task": "Group dinner planning",
                "description": "Healthy, authentic, and Mexican preferences"
            },
            {
                "users": ["eve", "jack"],
                "task": "Family-friendly dining",
                "description": "Budget-conscious with kids meets hearty meals"
            }
        ]
        
        for scenario in collaboration_scenarios:
            print(f"\n  🍽️  Scenario: {scenario['description']}")
            
            # Use collaboration tracker
            with CollaborationTracker(scenario["task"], scenario["users"]) as collab_id:
                result = await system.collaborate_users(
                    scenario["users"], 
                    scenario["task"], 
                    "New York City"
                )
                
                if result.get("collaboration_success", False):
                    print(f"    ✅ Collaboration successful!")
                    print(f"    🏆 Top recommendation: {result['recommended_restaurants'][0]['restaurant']}")
                    print(f"    🎯 Compatibility score: {result['recommended_restaurants'][0]['compatibility_score']:.3f}")
                    print(f"    📊 Total restaurants found: {result['total_restaurants_found']}")
                else:
                    print(f"    ❌ Collaboration failed: {result.get('error', 'Unknown error')}")
        
        # Step 6: Show system performance metrics
        print("\n📈 Step 6: System Performance Metrics")
        performance = monitor.get_performance_summary()
        print(f"Total Requests: {performance['total_requests']}")
        print(f"Average Response Time: {performance['avg_response_time_ms']:.2f}ms")
        print(f"P95 Response Time: {performance['p95_response_time_ms']:.2f}ms")
        print(f"System Health: {performance['system_health']}")
        print(f"Active Collaborations: {performance['active_collaborations']}")
        print(f"Completed Collaborations: {performance['completed_collaborations']}")
        
        # Step 7: Export metrics
        print("\n💾 Step 7: Exporting Metrics")
        monitor.export_metrics("a2a_demo_metrics.json")
        print("✅ Metrics exported to 'a2a_demo_metrics.json'")
        
        # Step 8: Show final system status
        print("\n🎊 Step 8: Final System Status")
        final_status = await system.get_system_status()
        print("System Status:")
        print(json.dumps(final_status, indent=2))
        
        print("\n🎉 A2A Agent Networking System Demo Complete!")
        print("=" * 50)
        
        # Instructions for next steps
        print("\n📋 Next Steps:")
        print("1. Set environment variables:")
        print("   - EXA_API_KEY: Your Exa API key")
        print("   - REDIS_URL: Redis connection URL")
        print("   - WANDB_API_KEY: Weights & Biases API key")
        print("   - OPENAI_API_KEY: OpenAI API key (optional)")
        print("2. Run in production mode:")
        print("   export A2A_PRODUCTION=true")
        print("   python run_a2a_system.py")
        print("3. Test with A2A CLI:")
        print("   google-a2a-cli --agent http://localhost:10002 --skill preference-matching")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        # Cleanup
        await system.stop_server()
        monitor.cleanup()

async def run_production_mode():
    """Run the A2A system in production mode."""
    print("🚀 Starting A2A System in Production Mode")
    print("=" * 50)
    
    system = A2ANetworkingSystem()
    
    try:
        # Load custom preferences if available
        custom_preferences = None
        if os.path.exists("user_preferences.json"):
            with open("user_preferences.json", "r") as f:
                custom_preferences = json.load(f)
                print(f"✅ Loaded custom preferences for {len(custom_preferences)} users")
        
        # Initialize system
        await system.initialize(custom_preferences)
        
        # Start server
        host = os.getenv("A2A_HOST", "0.0.0.0")
        port = int(os.getenv("A2A_PORT", "10002"))
        
        print(f"🌐 Starting A2A server on {host}:{port}")
        print("📡 Server supports HTTP/3 + gRPC")
        print("🔧 Use Ctrl+C to stop the server")
        
        await system.start_server(host, port)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown signal received")
    except Exception as e:
        print(f"❌ Production server error: {e}")
        raise
    finally:
        await system.stop_server()
        monitor.cleanup()

def main():
    """Main entry point."""
    # Check if running in production mode
    if os.getenv("A2A_PRODUCTION", "false").lower() == "true":
        asyncio.run(run_production_mode())
    else:
        asyncio.run(run_a2a_demo())

if __name__ == "__main__":
    main() 