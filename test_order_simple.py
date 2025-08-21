#!/usr/bin/env python3
import requests
import json
import sys

def test_create_order():
    """Test create_order with variant ID 42908272656467 and email VamsiKrishna@gmail.com"""
    
    url = "http://localhost:8001/api/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_order",
            "arguments": {
                "order": {
                    "line_items": [
                        {
                            "variant_id": 42908272656467,
                            "quantity": 1
                        }
                    ],
                    "customer": {
                        "email": "VamsiKrishna@gmail.com"
                    },
                    "financial_status": "paid",
                    "test": True
                }
            }
        },
        "id": 1
    }
    
    print("Testing Create Order MCP Tool")
    print("=" * 40)
    print(f"Variant ID: 42908272656467")
    print(f"Email: VamsiKrishna@gmail.com")
    print("=" * 40)
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            # Extract order data from MCP response
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and "text" in content[0]:
                    order_data = json.loads(content[0]["text"])
                    
                    if "error" in order_data:
                        print(f"\nERROR: {order_data['error']}")
                        if "details" in order_data:
                            print(f"Details: {order_data['details']}")
                    elif "order" in order_data:
                        order = order_data["order"]
                        print(f"\nSUCCESS!")
                        print(f"Order ID: {order.get('id')}")
                        print(f"Order Number: {order.get('name')}")
                        print(f"Total: {order.get('total_price')}")
                        print(f"Status: {order.get('financial_status')}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to MCP server at localhost:8001")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_create_order()
