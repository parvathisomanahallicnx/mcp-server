import requests
import json

# Test the Shopify MCP Server
BASE_URL = "http://localhost:8001"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tools_list():
    """Test the tools/list MCP endpoint"""
    print("\n=== Testing tools/list Endpoint ===")
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    try:
        response = requests.post(f"{BASE_URL}/api/mcp", json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200 and "result" in result
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_create_order_tool():
    """Test the create_order tool"""
    print("\n=== Testing create_order Tool ===")
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "create_order",
            "arguments": {
                "order": {
                    "line_items": [
                        {
                            "variant_id": 42910880890963,
                            "quantity": 1,
                            "title": "Test Product",
                            "price": 100.0
                        }
                    ],
                    "customer": {
                        "email": "test@example.com"
                    },
                    "financial_status": "paid",
                    "test": True
                }
            }
        },
        "id": 2
    }
    try:
        response = requests.post(f"{BASE_URL}/api/mcp", json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_order_status_tool():
    """Test the get_order_status tool"""
    print("\n=== Testing get_order_status Tool ===")
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_order_status",
            "arguments": {
                "order_id": 5904242344019
            }
        },
        "id": 3
    }
    try:
        response = requests.post(f"{BASE_URL}/api/mcp", json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_tool():
    """Test calling an invalid tool"""
    print("\n=== Testing Invalid Tool ===")
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "invalid_tool",
            "arguments": {}
        },
        "id": 4
    }
    try:
        response = requests.post(f"{BASE_URL}/api/mcp", json=payload)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return response.status_code == 200 and "error" in result
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Shopify MCP Server Testing")
    print("=" * 50)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Tools List", test_tools_list),
        ("Create Order Tool", test_create_order_tool),
        ("Get Order Status Tool", test_get_order_status_tool),
        ("Invalid Tool Error", test_invalid_tool)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
