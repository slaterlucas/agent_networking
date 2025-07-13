#!/usr/bin/env python3
"""
LLM Router Test Script

This script demonstrates the LLM-powered router functionality with different LLM providers.
"""

import asyncio
import json
import os
from router.router import LLMRouter

def test_llm_router():
    """Test the LLM router with different providers and scenarios"""
    
    # Test scenarios
    test_scenarios = [
        "Alice needs to talk to Bob for restaurant recommendations",
        "Alice needs help with food",
        "Bob wants dining suggestions",
        "Alice and Bob want to collaborate on Japanese restaurant selection",
        "Charlie needs to test restaurant features",
        "Diana and Alice want to find vegetarian restaurants",
        "I need help setting up communication between Alice and Bob",
        "Alice requires restaurant recommendations for tonight"
    ]
    
    print("🤖 LLM Router Test")
    print("=" * 60)
    
    # Test with different providers
    providers = []
    
    # Check if OpenAI is available
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    
    if not providers:
        print("⚠️  No OpenAI API key found. Testing pattern matching only.")
        providers = ["pattern_matching"]
    
    for provider in providers:
        print(f"\n🔧 Testing with {provider.upper()}")
        print("-" * 40)
        
        # Create router with specific provider
        if provider == "pattern_matching":
            router = LLMRouter(use_llm=False)
        else:
            router = LLMRouter(use_llm=True)
        
        for i, scenario in enumerate(test_scenarios[:3], 1):  # Test first 3 scenarios
            print(f"\n📝 Test {i}: {scenario}")
            
            try:
                # Parse requirements
                parsed = router.parse_requirements(scenario)
                print(f"✅ Result: {json.dumps(parsed, indent=2)}")
                
                # Generate commands
                commands = router.generate_commands(parsed)
                print(f"🔧 Commands: {len(commands)} generated")
                
                # Generate test commands
                test_commands = router.generate_test_commands(parsed)
                if test_commands:
                    print(f"🧪 Test: {len(test_commands)} test commands generated")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print()

def test_comparison():
    """Compare LLM vs pattern matching results"""
    
    print("\n🔍 Comparison Test: LLM vs Pattern Matching")
    print("=" * 60)
    
    test_cases = [
        "Alice needs to talk to Bob for restaurant recommendations",
        "I want Charlie to help with dining suggestions",
        "Alice and Diana should collaborate on finding sushi restaurants"
    ]
    
    # Test with pattern matching
    pattern_router = LLMRouter(use_llm=False)
    
    # Test with LLM (if available)
    llm_router = None
    if os.getenv("OPENAI_API_KEY"):
        llm_router = LLMRouter(use_llm=True)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case}")
        print("-" * 40)
        
        # Pattern matching result
        pattern_result = pattern_router.parse_requirements(test_case)
        print(f"🔢 Pattern Matching: {json.dumps(pattern_result, indent=2)}")
        
        # LLM result (if available)
        if llm_router:
            llm_result = llm_router.parse_requirements(test_case)
            print(f"🤖 LLM: {json.dumps(llm_result, indent=2)}")
            
            # Compare results
            differences = []
            for key in pattern_result:
                if pattern_result[key] != llm_result[key]:
                    differences.append(f"{key}: pattern={pattern_result[key]} vs llm={llm_result[key]}")
            
            if differences:
                print(f"⚠️  Differences: {', '.join(differences)}")
            else:
                print("✅ Results match!")
        else:
            print("⚠️  No LLM API key available for comparison")

def main():
    """Main entry point"""
    print("🧪 LLM Router Testing Suite")
    print("=" * 60)
    
    # Check for API keys
    print("\n🔑 API Key Status:")
    print(f"OpenAI: {'✅ Available' if os.getenv('OPENAI_API_KEY') else '❌ Not found'}")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n💡 To test LLM functionality, set environment variable:")
        print("   export OPENAI_API_KEY='your_openai_key'")
    
    # Run tests
    test_llm_router()
    test_comparison()
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    main() 