"""
Test to show the actual dummy responses
"""

import asyncio
import json
from shopify_mcp_server import create_order, get_order_status

async def main():
    print("=" * 70)
    print("DUMMY RESPONSE DEMO")
    print("=" * 70)
    print("\nShowing what successful responses look like with dummy data...\n")
    
    # Test create_order
    print("\n" + "=" * 70)
    print("1. CREATE ORDER - Dummy Response")
    print("=" * 70)
    
    result = await create_order(
        line_items=[
            {
                "variant_id": 12345,
                "quantity": 2,
                "title": "Cool T-Shirt",
                "price": 29.99
            },
            {
                "variant_id": 67890,
                "quantity": 1,
                "title": "Awesome Hat",
                "price": 19.99
            }
        ],
        customer_email="john@example.com",
        financial_status="paid",
        test=True
    )
    
    print(result)
    
    # Test get_order_status
    print("\n" + "=" * 70)
    print("2. GET ORDER STATUS - Dummy Response")
    print("=" * 70)
    
    result = await get_order_status(order_id=12345)
    
    print(result)
    
    print("\n" + "=" * 70)
    print("Note: 'dummy_mode': true indicates these are mock responses")
    print("Set USE_DUMMY_RESPONSES=false in .env to disable dummy mode")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
