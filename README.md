# Shopify MCP Server

A Model Context Protocol (MCP) server for Shopify order management using the official MCP Python SDK.

## Features
- ✅ **MCP-Compliant**: Follows official MCP specification
- 🛠️ **Two Tools**: Create orders and check order status via Shopify Admin REST API
- 🌐 **Remote Access**: SSE transport for cloud deployment
- 🔒 **Secure**: Environment-based credential management

## Available Tools

### 1. `create_order`
Create new Shopify orders with line items and customer information.

**Parameters:**
- `line_items` (array, required): Product items to order
- `customer_email` (string, optional): Customer email
- `financial_status` (string, optional): Payment status (default: "pending")
- `test` (boolean, optional): Create as test order (default: true)

### 2. `get_order_status`
Retrieve complete order details by order ID.

**Parameters:**
- `order_id` (integer, required): Shopify order ID

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Shopify Admin API access token
- Shopify store URL

### Local Setup

```bash
# Clone the repository
cd mcp-server

# Create and activate virtual environment (recommended)
python -m venv mcpserver
mcpserver\Scripts\activate  # Windows
# source mcpserver/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with:
SHOPIFY_ADMIN_API_BASE_URL=https://your-store.myshopify.com/admin/api/2025-07
SHOPIFY_ACCESS_TOKEN=your_access_token_here
USE_DUMMY_RESPONSES=true  # Optional: returns mock data when API fails (for testing)

# Run the server
python shopify_mcp_server.py
```

## Testing Mode (Dummy Responses)

For development and testing without valid Shopify credentials, enable dummy response mode:

```bash
# In .env file
USE_DUMMY_RESPONSES=true
```

When enabled:
- ✅ API errors return **realistic mock data** instead of error messages
- ✅ Test tools without valid Shopify store credentials
- ✅ See what successful responses look like
- ✅ All responses include `"dummy_mode": true` flag

**Demo:**
```bash
python demo_dummy_responses.py
```

**Example dummy response:**
```json
{
  "success": true,
  "dummy_mode": true,
  "order_id": 9999999999,
  "order_number": 1001,
  "financial_status": "paid",
  "total_price": "79.97",
  "note": "This is a dummy response for testing purposes"
}
```

**Disable for production:**
```bash
USE_DUMMY_RESPONSES=false  # or remove the variable entirely
```

## Usage with MCP Clients

### Claude Desktop Integration

Add to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "shopify": {
      "command": "python",
      "args": ["C:\\path\\to\\mcp-server\\shopify_mcp_server.py"],
      "env": {
        "SHOPIFY_ADMIN_API_BASE_URL": "https://your-store.myshopify.com/admin/api/2025-07",
        "SHOPIFY_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

Restart Claude Desktop, and you'll see the Shopify tools available.

### MCP Inspector (Testing)

Test your server with the official MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python shopify_mcp_server.py
```

This opens a web interface to test tool discovery and execution.

## Remote Deployment

The server uses **SSE (Server-Sent Events) transport** for remote access, making it compatible with cloud platforms.

### Railway Deployment

1. **Fork/Clone this repository**
2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository

3. **Set Environment Variables** in Railway dashboard:
   ```
   SHOPIFY_ADMIN_API_BASE_URL=https://your-store.myshopify.com/admin/api/2025-07
   SHOPIFY_ACCESS_TOKEN=your_access_token_here
   ```

4. **Deploy**: Railway auto-deploys from `Procfile`

Your MCP server will be available at: `https://your-app.up.railway.app`

### Render Deployment

1. **Connect GitHub repo** to Render
2. **Create new Web Service**
3. **Set environment variables**
4. **Set start command**: `python shopify_mcp_server.py`

### Other Platforms (Fly.io, Heroku, etc.)

The server works on any platform supporting Python web services. Use the start command:
```bash
python shopify_mcp_server.py
```

## Transport Options

The server supports two transport modes (configured in code):

```python
# SSE Transport (remote access, default)
mcp.run(transport="sse")

# STDIO Transport (local only, for Claude Desktop)
mcp.run(transport="stdio")
```

**Current configuration**: SSE (remote deployment)

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SHOPIFY_ADMIN_API_BASE_URL` | Shopify Admin API endpoint | `https://store.myshopify.com/admin/api/2025-07` |
| `SHOPIFY_ACCESS_TOKEN` | Admin API access token | `shpat_xxxxx` |
| `USE_DUMMY_RESPONSES` | Enable mock responses for testing (optional) | `true` or `false` (default: `false`) |


## Security Best Practices

⚠️ **Important Security Notes:**

- **Never commit `.env` files** to version control (already in `.gitignore`)
- **Use environment variables** on hosting platforms
- **Rotate access tokens** regularly
- **Enable HTTPS** in production (automatic on Railway/Render)
- **Restrict API scopes** to minimum required permissions

## Troubleshooting

### "SHOPIFY_ACCESS_TOKEN not set"
- Verify `.env` file exists and contains the token
- Check environment variables in your deployment platform

### "Order not found" (404)
- Verify the order ID is correct (use numeric ID, not order number)
- Check API access token has permission to read orders

### Tools not appearing in Claude Desktop
- Verify configuration file path is correct
- Check Python path in the `command` field
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for errors

## Development

### Project Structure
```
mcp-server/
├── shopify_mcp_server.py   # Main MCP server
├── requirements.txt         # Python dependencies
├── .env                     # Local environment variables (gitignored)
├── Procfile                # Railway/Heroku deployment
└── README.md               # This file
```

### Testing

Use MCP Inspector for development testing:
```bash
npx @modelcontextprotocol/inspector python shopify_mcp_server.py
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Shopify Admin API](https://shopify.dev/docs/api/admin-rest)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

## License

MIT

