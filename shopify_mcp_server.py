import os
import json
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read from environment variables for security
SHOPIFY_ADMIN_API_BASE_URL = os.getenv(
    "SHOPIFY_ADMIN_API_BASE_URL", 
    "https://YOUR_STORE.myshopify.com/admin/api/2025-07"
)
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Enable dummy responses for testing (returns mock data when API fails)
USE_DUMMY_RESPONSES = os.getenv("USE_DUMMY_RESPONSES", "false").lower() in ("true", "1", "yes")

# Initialize FastMCP server (host=0.0.0.0 allows any Host header for cloud deployment)
mcp = FastMCP("shopify-orders", host="0.0.0.0")

# Expose ASGI app for uvicorn deployment (Render, Railway, etc.)
# Using Streamable HTTP transport (recommended for MCP SDK >= 1.2.0)
app = mcp.streamable_http_app()

async def _make_shopify_request(
    method: str, 
    endpoint: str, 
    json_data: dict | None = None
) -> dict[str, Any]:
    """
    Make a request to the Shopify Admin API with proper error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path (e.g., '/orders.json')
        json_data: Optional JSON payload for POST/PUT requests
        
    Returns:
        Response JSON data
        
    Raises:
        ValueError: If access token is missing
        httpx.HTTPError: If the request fails
    """
    if not SHOPIFY_ACCESS_TOKEN:
        raise ValueError("SHOPIFY_ACCESS_TOKEN environment variable is not set")
    
    url = f"{SHOPIFY_ADMIN_API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method.upper() == "GET":
            response = await client.get(url, headers=headers)
        elif method.upper() == "POST":
            response = await client.post(url, json=json_data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def create_order(
    line_items: list[dict],
    customer_email: str | None = None,
    financial_status: str = "pending",
    test: bool = True
) -> str:
    """
    Create a Shopify order via Admin REST API.
    
    This tool creates a new order in your Shopify store with the specified line items
    and customer information. By default, orders are created as test orders.
    
    Args:
        line_items: Array of line item objects. Each line item should contain:
            - variant_id (int): The Shopify variant ID
            - quantity (int): Quantity to order
            - title (str, optional): Product title
            - price (float, optional): Price per item
        customer_email: Optional customer email address
        financial_status: Financial status of the order (default: "pending")
            Options: "pending", "authorized", "paid", "partially_paid", "refunded", "voided"
        test: Whether to create as a test order (default: True)
    
    Returns:
        JSON string with the created order details including order ID, status, and line items
        
    Example:
        create_order(
            line_items=[{
                "variant_id": 42910880890963,
                "quantity": 2,
                "title": "Cool T-Shirt",
                "price": 29.99
            }],
            customer_email="customer@example.com",
            financial_status="paid",
            test=True
        )
    """
    # Build the order payload
    order_payload = {
        "order": {
            "line_items": line_items,
            "financial_status": financial_status,
            "test": test
        }
    }
    
    # Add customer email if provided
    if customer_email:
        order_payload["order"]["customer"] = {"email": customer_email}
    
    try:
        result = await _make_shopify_request("POST", "/orders.json", order_payload)
        
        # Format the response nicely
        order = result.get("order", {})
        return json.dumps({
            "success": True,
            "order_id": order.get("id"),
            "order_number": order.get("order_number"),
            "financial_status": order.get("financial_status"),
            "total_price": order.get("total_price"),
            "currency": order.get("currency"),
            "created_at": order.get("created_at"),
            "test_order": order.get("test"),
            "line_items_count": len(order.get("line_items", [])),
            "customer_email": order.get("customer", {}).get("email")
        }, indent=2)
        
    except ValueError as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response for testing
            from datetime import datetime
            total = sum(item.get("price", 0) * item.get("quantity", 1) for item in line_items)
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": 9999999999,
                "order_number": 1001,
                "financial_status": financial_status,
                "total_price": f"{total:.2f}",
                "currency": "USD",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "test_order": test,
                "line_items_count": len(line_items),
                "customer_email": customer_email,
                "note": "This is a dummy response for testing purposes"
            }, indent=2)
        return json.dumps({
            "success": False,
            "error": "Configuration Error",
            "message": str(e)
        }, indent=2)
    except httpx.HTTPStatusError as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response for testing
            from datetime import datetime
            total = sum(item.get("price", 0) * item.get("quantity", 1) for item in line_items)
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": 9999999999,
                "order_number": 1001,
                "financial_status": financial_status,
                "total_price": f"{total:.2f}",
                "currency": "USD",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "test_order": test,
                "line_items_count": len(line_items),
                "customer_email": customer_email,
                "note": "This is a dummy response for testing purposes (API returned error)"
            }, indent=2)
        return json.dumps({
            "success": False,
            "error": "Shopify API Error",
            "status_code": e.response.status_code,
            "message": str(e),
            "response_body": e.response.text
        }, indent=2)
    except Exception as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response for testing
            from datetime import datetime
            total = sum(item.get("price", 0) * item.get("quantity", 1) for item in line_items)
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": 9999999999,
                "order_number": 1001,
                "financial_status": financial_status,
                "total_price": f"{total:.2f}",
                "currency": "USD",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "test_order": test,
                "line_items_count": len(line_items),
                "customer_email": customer_email,
                "note": "This is a dummy response for testing purposes"
            }, indent=2)
        return json.dumps({
            "success": False,
            "error": "Unexpected Error",
            "message": str(e)
        }, indent=2)


@mcp.tool()
async def get_order_status(order_id: int) -> str:
    """
    Get the status and details of a Shopify order by order ID.
    
    This tool retrieves complete order information including current status,
    fulfillment details, line items, customer information, and payment status.
    
    Args:
        order_id: The Shopify order ID (numeric ID, not order number)
    
    Returns:
        JSON string with comprehensive order details including:
        - Order status and financial status
        - Fulfillment status
        - Line items with quantities and prices
        - Customer information
        - Total price and currency
        - Timestamps
        
    Example:
        get_order_status(5904242344019)
    """
    try:
        result = await _make_shopify_request("GET", f"/orders/{order_id}.json")
        
        # Extract and format key order information
        order = result.get("order", {})
        
        # Format line items
        line_items = []
        for item in order.get("line_items", []):
            line_items.append({
                "title": item.get("title"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "variant_id": item.get("variant_id"),
                "fulfillment_status": item.get("fulfillment_status")
            })
        
        # Format fulfillments
        fulfillments = []
        for fulfillment in order.get("fulfillments", []):
            fulfillments.append({
                "status": fulfillment.get("status"),
                "tracking_company": fulfillment.get("tracking_company"),
                "tracking_number": fulfillment.get("tracking_number"),
                "created_at": fulfillment.get("created_at")
            })
        
        return json.dumps({
            "success": True,
            "order_id": order.get("id"),
            "order_number": order.get("order_number"),
            "financial_status": order.get("financial_status"),
            "fulfillment_status": order.get("fulfillment_status"),
            "total_price": order.get("total_price"),
            "currency": order.get("currency"),
            "created_at": order.get("created_at"),
            "updated_at": order.get("updated_at"),
            "cancelled_at": order.get("cancelled_at"),
            "test_order": order.get("test"),
            "customer": {
                "email": order.get("customer", {}).get("email"),
                "first_name": order.get("customer", {}).get("first_name"),
                "last_name": order.get("customer", {}).get("last_name")
            },
            "line_items": line_items,
            "fulfillments": fulfillments,
            "tags": order.get("tags"),
            "note": order.get("note")
        }, indent=2)
        
    except ValueError as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response
            from datetime import datetime, timedelta
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": order_id,
                "order_number": 1001,
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "total_price": "150.00",
                "currency": "USD",
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "cancelled_at": None,
                "test_order": True,
                "customer": {
                    "email": "customer@example.com",
                    "first_name": "Test",
                    "last_name": "Customer"
                },
                "line_items": [
                    {
                        "title": "Sample Product",
                        "quantity": 2,
                        "price": "75.00",
                        "variant_id": 12345,
                        "fulfillment_status": "fulfilled"
                    }
                ],
                "fulfillments": [
                    {
                        "status": "success",
                        "tracking_company": "USPS",
                        "tracking_number": "9400111111111111111111",
                        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                    }
                ],
                "tags": "test, dummy",
                "note": "This is a dummy response for testing purposes"
            }, indent=2)
        return json.dumps({
            "success": False,
            "error": "Configuration Error",
            "message": str(e)
        }, indent=2)
    except httpx.HTTPStatusError as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response
            from datetime import datetime, timedelta
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": order_id,
                "order_number": 1001,
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "total_price": "150.00",
                "currency": "USD",
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "cancelled_at": None,
                "test_order": True,
                "customer": {
                    "email": "customer@example.com",
                    "first_name": "Test",
                    "last_name": "Customer"
                },
                "line_items": [
                    {
                        "title": "Sample Product",
                        "quantity": 2,
                        "price": "75.00",
                        "variant_id": 12345,
                        "fulfillment_status": "fulfilled"
                    }
                ],
                "fulfillments": [
                    {
                        "status": "success",
                        "tracking_company": "USPS",
                        "tracking_number": "9400111111111111111111",
                        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                    }
                ],
                "tags": "test, dummy",
                "note": "This is a dummy response for testing purposes (API returned error)"
            }, indent=2)
        
        error_response = {
            "success": False,
            "error": "Shopify API Error",
            "status_code": e.response.status_code,
            "message": str(e)
        }
        
        # Add helpful message for 404
        if e.response.status_code == 404:
            error_response["helpful_message"] = f"Order ID {order_id} not found. Please verify the order ID is correct."
        
        return json.dumps(error_response, indent=2)
    except Exception as e:
        if USE_DUMMY_RESPONSES:
            # Return dummy successful response
            from datetime import datetime, timedelta
            return json.dumps({
                "success": True,
                "dummy_mode": True,
                "order_id": order_id,
                "order_number": 1001,
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "total_price": "150.00",
                "currency": "USD",
                "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "cancelled_at": None,
                "test_order": True,
                "customer": {
                    "email": "customer@example.com",
                    "first_name": "Test",
                    "last_name": "Customer"
                },
                "line_items": [
                    {
                        "title": "Sample Product",
                        "quantity": 2,
                        "price": "75.00",
                        "variant_id": 12345,
                        "fulfillment_status": "fulfilled"
                    }
                ],
                "fulfillments": [
                    {
                        "status": "success",
                        "tracking_company": "USPS",
                        "tracking_number": "9400111111111111111111",
                        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                    }
                ],
                "tags": "test, dummy",
                "note": "This is a dummy response for testing purposes"
            }, indent=2)
        return json.dumps({
            "success": False,
            "error": "Unexpected Error",
            "message": str(e)
        }, indent=2)


if __name__ == "__main__":
    # Auto-detect transport mode:
    # - STDIO for local testing (MCP Inspector, Claude Desktop)
    # - SSE for remote deployment (Railway, Render)
    transport_mode = os.getenv("MCP_TRANSPORT", "stdio").lower()
    mcp.run(transport=transport_mode)
