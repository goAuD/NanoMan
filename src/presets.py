"""
NanoMan - API Presets & Templates
Local templates for common APIs and auth patterns.
No cloud integration - just convenience presets.

Part of the Nano Product Family.
"""

# === Auth Presets ===
AUTH_PRESETS = {
    "none": {
        "name": "No Auth",
        "headers": {},
        "description": "No authentication"
    },
    "bearer": {
        "name": "Bearer Token",
        "headers": {"Authorization": "Bearer <YOUR_TOKEN>"},
        "description": "JWT or OAuth2 bearer token",
        "docs": "https://jwt.io/"
    },
    "basic": {
        "name": "Basic Auth",
        "headers": {"Authorization": "Basic <BASE64_CREDENTIALS>"},
        "description": "Base64 encoded username:password",
        "docs": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication"
    },
    "api_key_header": {
        "name": "API Key (Header)",
        "headers": {"X-Api-Key": "<YOUR_API_KEY>"},
        "description": "API key in X-Api-Key header"
    },
    "api_key_auth": {
        "name": "API Key (Authorization)",
        "headers": {"Authorization": "ApiKey <YOUR_API_KEY>"},
        "description": "API key in Authorization header"
    },
}


# === API Templates ===
API_TEMPLATES = {
    "localhost": {
        "name": "Localhost",
        "base_url": "http://localhost:8080",
        "auth": "none",
        "description": "Local development server",
        "examples": [
            {"method": "GET", "path": "/api/health", "desc": "Health check"},
            {"method": "GET", "path": "/api/status", "desc": "Status endpoint"},
            {"method": "GET", "path": "/api/v1/users", "desc": "List users"},
        ]
    },
    "microsoft_graph": {
        "name": "Microsoft Graph API",
        "base_url": "https://graph.microsoft.com/v1.0",
        "auth": "bearer",
        "description": "Microsoft 365 & Azure AD API",
        "docs": "https://learn.microsoft.com/en-us/graph/api/overview",
        "examples": [
            {"method": "GET", "path": "/me", "desc": "Get current user"},
            {"method": "GET", "path": "/me/messages", "desc": "List emails"},
            {"method": "GET", "path": "/me/drive/root/children", "desc": "OneDrive files"},
            {"method": "GET", "path": "/me/calendar/events", "desc": "Calendar events"},
        ]
    },
    "github": {
        "name": "GitHub API",
        "base_url": "https://api.github.com",
        "auth": "bearer",
        "description": "GitHub REST API v3",
        "docs": "https://docs.github.com/en/rest",
        "examples": [
            {"method": "GET", "path": "/user", "desc": "Authenticated user"},
            {"method": "GET", "path": "/user/repos", "desc": "List repositories"},
            {"method": "GET", "path": "/repos/:owner/:repo", "desc": "Get repository"},
            {"method": "GET", "path": "/repos/:owner/:repo/issues", "desc": "List issues"},
        ]
    },
    "jsonplaceholder": {
        "name": "JSONPlaceholder",
        "base_url": "https://jsonplaceholder.typicode.com",
        "auth": "none",
        "description": "Free fake REST API for testing",
        "docs": "https://jsonplaceholder.typicode.com/",
        "examples": [
            {"method": "GET", "path": "/posts", "desc": "List posts"},
            {"method": "GET", "path": "/posts/1", "desc": "Get post by ID"},
            {"method": "POST", "path": "/posts", "desc": "Create post"},
            {"method": "GET", "path": "/users", "desc": "List users"},
            {"method": "GET", "path": "/comments?postId=1", "desc": "Comments for post"},
        ]
    },
    "httpbin": {
        "name": "HTTPBin",
        "base_url": "https://httpbin.org",
        "auth": "none",
        "description": "HTTP request & response testing",
        "docs": "https://httpbin.org/",
        "examples": [
            {"method": "GET", "path": "/get", "desc": "Returns GET data"},
            {"method": "POST", "path": "/post", "desc": "Returns POST data"},
            {"method": "GET", "path": "/headers", "desc": "Returns request headers"},
            {"method": "GET", "path": "/ip", "desc": "Returns origin IP"},
            {"method": "GET", "path": "/status/418", "desc": "I'm a teapot!"},
        ]
    },
    "reqres": {
        "name": "ReqRes",
        "base_url": "https://reqres.in/api",
        "auth": "none",
        "description": "Fake API for testing with auth flows",
        "docs": "https://reqres.in/",
        "examples": [
            {"method": "GET", "path": "/users", "desc": "List users (paginated)"},
            {"method": "GET", "path": "/users/2", "desc": "Single user"},
            {"method": "POST", "path": "/register", "desc": "Register user"},
            {"method": "POST", "path": "/login", "desc": "Login"},
        ]
    },
}


def get_auth_preset_names() -> list:
    """Return list of auth preset names for UI dropdown."""
    return [preset["name"] for preset in AUTH_PRESETS.values()]


def get_api_template_names() -> list:
    """Return list of API template names for UI."""
    return [template["name"] for template in API_TEMPLATES.values()]


def get_auth_preset_by_name(name: str) -> dict:
    """Get auth preset by display name."""
    for key, preset in AUTH_PRESETS.items():
        if preset["name"] == name:
            return preset
    return AUTH_PRESETS["none"]


def get_api_template_by_name(name: str) -> dict:
    """Get API template by display name."""
    for key, template in API_TEMPLATES.items():
        if template["name"] == name:
            return template
    return API_TEMPLATES["localhost"]
