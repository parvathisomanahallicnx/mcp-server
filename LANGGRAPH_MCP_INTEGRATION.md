# LangGraph Agent with MCP Server Integration

## Overview

This document explains how the LangGraph agent workflow integrates with the refactored MCP server for Shopify order management.

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# MCP Server Configuration
USE_LOCAL_MCP=true  # Use local MCP server directly (recommended for development)
ORDER_MCP_URL=http://localhost:8000/mcp  # For remote SSE transport

# Shopify API (already configured in shopify_mcp_server.py)
SHOPIFY_ADMIN_API_BASE_URL=https://your-store.myshopify.com/admin/api/2025-07
SHOPIFY_ACCESS_TOKEN=your_access_token
USE_DUMMY_RESPONSES=true  # Enable dummy responses for testing
```

## Integration Modes

### 1. Local Direct Mode (Recommended for Development)

Set `USE_LOCAL_MCP=true` to call MCP server tools directly:

**Benefits:**
- No HTTP overhead
- Faster execution
- Easier debugging
- Works with dummy responses

**How it works:**
```python
from shopify_mcp_server import create_order, get_order_status
result = await create_order(line_items=..., customer_email=...)
```

### 2. HTTP/SSE Mode (For Production)

Set `USE_LOCAL_MCP=false` and configure `ORDER_MCP_URL`:

**Benefits:**
- Server can be deployed remotely
- Multiple clients can connect
- Standard MCP protocol

**How it works:**
```python
# Calls via JSON-RPC over HTTP
POST http://localhost:8000/mcp
{
  "method": "tools/call",
  "params": {
    "name": "create_order",
    "arguments": {...}
  }
}
```

## Updated Tool Signatures

### create_order

**Old signature (nested):**
```python
{
  "order": {
    "line_items": [...],
    "customer": {"email": "..."},
    "financial_status": "paid",
    "test": true
  }
}
```

**New signature (flat):**
```python
{
  "line_items": [
    {
      "variant_id": 12345,
      "quantity": 1,
      "title": "Product Name",
      "price": 29.99
    }
  ],
  "customer_email": "user@example.com",
  "financial_status": "paid",
  "test": true
}
```

### get_order_status

**Signature (unchanged):**
```python
{
  "order_id": 12345
}
```

## Testing

### Test with Dummy Responses

1. Enable dummy mode in `.env`:
   ```bash
   USE_DUMMY_RESPONSES=true
   USE_LOCAL_MCP=true
   ```

2. Run the LangGraph agent:
   ```bash
   python langgraph_agent_workflow.py
   ```

3. Send test queries:
   ```
   "I want to buy product variant 12345 with email test@example.com"
   "What's the status of order 12345?"
   ```

### Test with Real Shopify API

1. Configure valid Shopify credentials in `.env`
2. Disable dummy mode: `USE_DUMMY_RESPONSES=false`
3. Use real variant IDs from your Shopify store

## Changes Made

1. **Added `call_mcp_server_local()`** - Direct function calls for local mode
2. **Updated `call_mcp_server()`** - Auto-detects mode (local vs HTTP)
3. **Updated `order_creation_node()`** - Uses new flat parameter structure
4. **Updated configuration** - Environment-based mode selection

## Deployment

### Local Development
```bash
USE_LOCAL_MCP=true
USE_DUMMY_RESPONSES=true
```

### Staging/Testing
```bash
USE_LOCAL_MCP=false
ORDER_MCP_URL=https://your-staging-mcp-server.com/mcp
USE_DUMMY_RESPONSES=false
```

### Production
```bash
USE_LOCAL_MCP=false
ORDER_MCP_URL=https://your-production-mcp-server.com/mcp
USE_DUMMY_RESPONSES=false
```

## Troubleshooting

### Issue: "Local MCP call error"

**Solution:** Ensure `shopify_mcp_server.py` is in the same directory as `langgraph_agent_workflow.py`

### Issue: "Invalid MCP response format"

**Check:**
1. MCP server is running (if using HTTP mode)
2. URL is correct in `ORDER_MCP_URL`
3. Server returned valid JSON

### Issue: "Tool returns error response"

**With dummy mode:**
- Check `USE_DUMMY_RESPONSES=true` in `.env`
- Restart the workflow after changing `.env`

**With real API:**
- Verify Shopify credentials
- Check variant IDs exist in your store
- Review server logs for API errors
