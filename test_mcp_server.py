import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the Shopify MCP Server using the MCP client SDK"""
    
    print("Shopify MCP Server Testing")
    print("=" * 60)
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["shopify_mcp_server.py"],
        env=None  # Will use .env file
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("\n[OK] Connected to MCP server")
            
            # Test 1: List available tools
            print("\n" + "=" * 60)
            print("Test 1: Listing Available Tools")
            print("=" * 60)
            
            tools = await session.list_tools()
            print(f"\nFound {len(tools.tools)} tools:")
            
            for tool in tools.tools:
                print(f"\n[TOOL] {tool.name}")
                print(f"   Description: {tool.description}")
                if hasattr(tool, 'inputSchema'):
                    print(f"   Input Schema: {json.dumps(tool.inputSchema, indent=2)}")
            
            # Test 2: Call create_order tool (with test data)
            print("\n" + "=" * 60)
            print("Test 2: Creating Test Order")
            print("=" * 60)
            
            try:
                result = await session.call_tool(
                    "create_order",
                    arguments={
                        "line_items": [
                            {
                                "variant_id": 42910880890963,
                                "quantity": 1,
                                "title": "Test Product",
                                "price": 100.0
                            }
                        ],
                        "customer_email": "test@example.com",
                        "financial_status": "paid",
                        "test": True
                    }
                )
                
                print("\n[OK] Create Order Response:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    
            except Exception as e:
                print(f"\n[ERROR] Error creating order: {e}")
            
            # Test 3: Call get_order_status tool
            print("\n" + "=" * 60)
            print("Test 3: Getting Order Status")
            print("=" * 60)
            
            # You can replace this with an actual order ID from your store
            test_order_id = 5904242344019
            
            try:
                result = await session.call_tool(
                    "get_order_status",
                    arguments={
                        "order_id": test_order_id
                    }
                )
                
                print(f"\n[OK] Order Status Response:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                        
            except Exception as e:
                print(f"\n[ERROR] Error getting order status: {e}")
            
            print("\n" + "=" * 60)
            print("[OK] All tests completed")
            print("=" * 60)


async def test_tool_discovery_only():
    """Quick test to just discover available tools"""
    
    print("Quick Tool Discovery Test")
    print("=" * 60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["shopify_mcp_server.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            tools = await session.list_tools()
            
            print(f"\n[OK] Server is running and exposing {len(tools.tools)} tools:\n")
            for tool in tools.tools:
                print(f"  • {tool.name}")
                print(f"    {tool.description}\n")


if __name__ == "__main__":
    import sys
    
    # Run quick discovery test by default
    # Use --full flag for full testing
    if "--full" in sys.argv:
        print("Running full test suite...\n")
        asyncio.run(test_mcp_server())
    else:
        print("Running quick discovery test (use --full for complete tests)...\n")
        asyncio.run(test_tool_discovery_only())
