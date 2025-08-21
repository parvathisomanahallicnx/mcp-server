# Shopify MCP Server

A FastAPI-based Model Context Protocol (MCP) server for Shopify order management.

## Features
- Create Shopify orders via Admin REST API
- Get order status and details
- MCP-compliant JSON-RPC interface

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

### 1. Fork/Clone this repository
### 2. Connect to Railway
1. Go to [Railway.app](https://railway.app)
2. Click "Deploy from GitHub repo"
3. Select this repository

### 3. Set Environment Variables
In Railway dashboard, add:
```
SHOPIFY_ADMIN_API_BASE_URL=https://your-store.myshopify.com/admin/api/2025-07
SHOPIFY_ACCESS_TOKEN=your_access_token_here
```

### 4. Deploy
Railway will automatically deploy your app at `https://your-app.railway.app`

## Other Free Hosting Options

### Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically

### Fly.io
```bash
flyctl launch
flyctl secrets set SHOPIFY_ACCESS_TOKEN=your_token
flyctl deploy
```

## Local Development

```bash
# Activate virtual environment
mcpserver\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python shopify_mcp_server.py
```

Server runs at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /tools` - List available MCP tools
- `POST /api/mcp` - MCP JSON-RPC endpoint

## Security Notes

⚠️ **Never commit `.env` files to version control**
- Use environment variables on hosting platforms
- Keep Shopify access tokens secure
- Enable HTTPS in production
