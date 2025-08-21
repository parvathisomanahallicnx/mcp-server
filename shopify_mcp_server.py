import os
import json
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read from environment variables for security
SHOPIFY_ADMIN_API_BASE_URL = os.getenv("SHOPIFY_ADMIN_API_BASE_URL", "https://YOUR_STORE.myshopify.com/admin/api/2025-07")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def create_order(order_payload: dict) -> dict:
    """Create a Shopify order via Admin REST API"""
    if not SHOPIFY_ACCESS_TOKEN:
        return {
            "error": "Missing configuration",
            "details": "Set SHOPIFY_ACCESS_TOKEN environment variable"
        }
    
    url = f"{SHOPIFY_ADMIN_API_BASE_URL}/orders.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(
            url,
            json=order_payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        return {"error": str(e), "response": response.text}
    except requests.RequestException as e:
        return {"error": "Request failed", "details": str(e)}

def get_order_status(order_id: int) -> dict:
    """Get order status via Shopify Admin REST API"""
    if not SHOPIFY_ACCESS_TOKEN:
        return {
            "error": "Missing configuration",
            "details": "Set SHOPIFY_ACCESS_TOKEN environment variable"
        }
    
    url = f"{SHOPIFY_ADMIN_API_BASE_URL}/orders/{order_id}.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        return {"error": str(e), "response": response.text}
    except requests.RequestException as e:
        return {"error": "Request failed", "details": str(e)}

# MCP Server Implementation
app = FastAPI(title="Shopify MCP Server", version="1.0.0")

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Any = None
    method: str
    params: Dict[str, Any] = {}

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Any = None
    result: Any = None
    error: Dict[str, Any] = None

def get_tools_definition():
    """Return MCP tools definition"""
    return {
        "tools": [
            {
                "name": "create_order",
                "description": "Create a Shopify order via Admin REST API. Requires an 'order' object with line_items, customer info, etc.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "object",
                            "properties": {
                                "line_items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "variant_id": {"type": "integer"},
                                            "quantity": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "price": {"type": "number"}
                                        }
                                    }
                                },
                                "customer": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"}
                                    }
                                },
                                "financial_status": {"type": "string"},
                                "test": {"type": "boolean"}
                            },
                            "required": ["line_items"]
                        }
                    },
                    "required": ["order"]
                }
            },
            {
                "name": "get_order_status",
                "description": "Get the status of a Shopify order by order ID. Returns order details including status, fulfillment info, and line items.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The Shopify order ID to retrieve status for"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        ]
    }

@app.post("/api/mcp")
async def mcp_endpoint(request: JSONRPCRequest):
    """MCP JSON-RPC endpoint"""
    try:
        if request.method == "tools/list":
            return JSONRPCResponse(
                id=request.id,
                result=get_tools_definition()
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            if tool_name == "create_order":
                # Call the create_order function
                result = create_order(arguments)
                
                # Format result as MCP content
                content = [{"type": "text", "text": json.dumps(result, indent=2)}]
                
                return JSONRPCResponse(
                    id=request.id,
                    result={"content": content}
                )
            
            elif tool_name == "get_order_status":
                # Extract order_id from arguments
                order_id = arguments.get("order_id")
                if not order_id:
                    return JSONRPCResponse(
                        id=request.id,
                        error={"code": -32602, "message": "Missing required parameter: order_id"}
                    )
                
                try:
                    order_id = int(order_id)
                except (ValueError, TypeError):
                    return JSONRPCResponse(
                        id=request.id,
                        error={"code": -32602, "message": "Invalid order_id: must be an integer"}
                    )
                
                # Call the get_order_status function
                result = get_order_status(order_id)
                
                # Format result as MCP content
                content = [{"type": "text", "text": json.dumps(result, indent=2)}]
                
                return JSONRPCResponse(
                    id=request.id,
                    result={"content": content}
                )
            
            else:
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Unknown tool: {tool_name}"}
                )
        
        else:
            return JSONRPCResponse(
                id=request.id,
                error={"code": -32601, "message": f"Unknown method: {request.method}"}
            )
    
    except Exception as e:
        return JSONRPCResponse(
            id=request.id,
            error={"code": -32603, "message": f"Internal error: {str(e)}"}
        )

@app.get("/")
async def root():
    """Health check endpoint"""
    tools = get_tools_definition()["tools"]
    return {
        "message": "Shopify MCP Server is running",
        "tools": len(tools),
        "available_tools": [tool["name"] for tool in tools]
    }

@app.get("/tools")
async def list_tools():
    """List available tools endpoint"""
    return get_tools_definition()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
