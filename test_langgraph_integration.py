"""
Test script for LangGraph MCP integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable local MCP mode for testing
os.environ["USE_LOCAL_MCP"] = "true"
os.environ["USE_DUMMY_RESPONSES"] = "true"

# Import the workflow
from langgraph_agent_workflow import (
    AgentState,
    order_creation_node,
    order_status_node
)

def test_order_creation():
    """Test order creation with new MCP server"""
    print("=" * 70)
    print("TEST 1: Order Creation")
    print("=" * 70)
    
    state = AgentState(
        user_message="I want to buy variant 12345 with email test@example.com",
        intent="order_creation"
    )
    
    result = order_creation_node(state)
    
    print("\nInput:")
    print(f"  Message: {state['user_message']}")
    
    print("\nOutput:")
    print(result.get("final_response", "No response"))
    
    return result

def test_order_status():
    """Test order status with new MCP server"""
    print("\n" + "=" * 70)
    print("TEST 2: Order Status")
    print("=" * 70)
    
    state = AgentState(
        user_message="What's the status of order 12345?",
        intent="order_status"
    )
    
    result = order_status_node(state)
    
    print("\nInput:")
    print(f"  Message: {state['user_message']}")
    
    print("\nOutput:")
    print(result.get("final_response", "No response"))
    
    return result

def main():
    print("\nLangGraph MCP Integration Test")
    print("=" * 70)
    print("Mode: Local Direct Calls")
    print("Dummy Responses: Enabled")
    print("=" * 70)
    
    try:
        # Test order creation
        result1 = test_order_creation()
        
        # Test order status
        result2 = test_order_status()
        
        print("\n" + "=" * 70)
        print("TESTS COMPLETED")
        print("=" * 70)
        
        # Check if both tests returned valid results
        has_order = result1.get("order_result") is not None
        has_status = result2.get("order_status") is not None
        
        if has_order and has_status:
            print("\n[SUCCESS] Both tests passed!")
            print("\nThe LangGraph agent is now integrated with the MCP server.")
        else:
            print("\n[WARNING] Some tests returned unexpected results")
            if not has_order:
                print("  - Order creation test failed")
            if not has_status:
                print("  - Order status test failed")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
