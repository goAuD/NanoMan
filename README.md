# NanoMan

**Offline API Testing Client**

NanoMan is a lightweight, privacy-focused API testing tool. No cloud, no bloat, just requests. Part of the **Nano Product Family**.

![Python](https://img.shields.io/badge/Made%20with-Python-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

![NanoMan Screenshot](nanoman.png)

## Features

* **Offline First:** Works without internet connection for local APIs
* **Privacy Focused:** No telemetry, no cloud, your data stays local
* **Full HTTP Support:** GET, POST, PUT, PATCH, DELETE methods
* **JSON Syntax Highlighting:** Color-coded JSON responses (keys, strings, numbers)
* **Request History:** Review and load previous requests with one click
* **Auth Presets:** Quick setup for Bearer, Basic Auth, API Key authentication
* **API Templates:** Pre-configured templates for Graph API, GitHub, HTTPBin, and more
* **Threaded Requests:** UI never freezes, even on slow connections
* **Security Focused:** Strict URL validation, no sensitive data in history

## Use Cases

### Backend Development
- Test your REST APIs during development
- Verify endpoints before frontend integration
- Debug API responses with pretty-printed JSON

### Learning & Education
- Explore public APIs without installing Postman
- Perfect for coding bootcamps and tutorials
- Understand HTTP methods and responses

### API Debugging
- Quick requests without browser DevTools
- Save custom headers for authenticated endpoints
- Test local development servers

## Requirements

* Python 3.8+
* Dependencies: `customtkinter`, `requests`

## Installation

```bash
# Clone repository
git clone https://github.com/goAuD/NanoMan.git
cd NanoMan

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Usage

1. Select HTTP method (GET, POST, PUT, PATCH, DELETE)
2. Enter API URL
3. (Optional) Add request body JSON in "Request Body" tab
4. (Optional) Add custom headers in "Headers" tab
5. (Optional) Use "Presets" tab for quick auth setup or API templates
6. Click **SEND** or press **Enter**

### Presets Tab

The Presets tab provides quick access to:

**Auth Presets:**
| Preset | Description |
|--------|-------------|
| No Auth | No authentication |
| Bearer Token | JWT / OAuth2 tokens |
| Basic Auth | Base64 username:password |
| API Key (Header) | X-Api-Key header |
| API Key (Authorization) | Authorization header |

**API Templates:**
| Template | Base URL |
|----------|----------|
| Localhost | `http://localhost:8080` |
| Microsoft Graph API | `https://graph.microsoft.com/v1.0` |
| GitHub API | `https://api.github.com` |
| JSONPlaceholder | `https://jsonplaceholder.typicode.com` |
| HTTPBin | `https://httpbin.org` |
| ReqRes | `https://reqres.in/api` |

## Project Structure

```
NanoMan/
├── main.py              # Entry point
├── version.py           # Version definition
├── nano_theme.py        # Nano Design System
├── requirements.txt     # Dependencies
├── src/
│   ├── __init__.py
│   ├── logic.py         # Business logic (API, validation)
│   ├── presets.py       # Auth presets & API templates
│   └── ui.py            # CustomTkinter UI
└── tests/
    ├── __init__.py
    └── test_logic.py    # Unit tests
```

## Data Storage

Request history is stored in your user config directory:
- **Windows:** `%USERPROFILE%\.nanoman\history.json`
- **Linux/macOS:** `~/.nanoman/history.json`

**Security:** Only method, URL, status code, and timing are saved. Headers and request body are never persisted to prevent leaking sensitive data.

## Security

| Threat | Prevention |
|--------|------------|
| XSS via URL | Only `http://` and `https://` allowed |
| JavaScript injection | `javascript:` URLs rejected |
| File access | `file://` URLs rejected |
| Credential leaks | Headers/body not saved to history |
| Request hanging | 10 second timeout |
| UI freeze | Threaded requests |

## Troubleshooting

### "Invalid or unsafe URL" error
- Make sure URL starts with `http://` or `https://`
- Check for typos in the URL
- Ensure no spaces in the URL

### Request times out
- Check if the server is running
- Try increasing timeout (edit `logic.py`, line 109)
- Verify network connection

### JSON not formatted
- Response must have `Content-Type: application/json`
- If plain text, it will display as-is

### Connection refused
- Server might not be running
- Check port number is correct
- Firewall might be blocking

## Running Tests

```bash
python -m pytest tests/ -v
```

## Part of Nano Product Family

This tool uses the [Nano Design System](https://github.com/goAuD/NanoServer/blob/main/DESIGN_SYSTEM.md) for consistent styling across lightweight developer tools.

## License

MIT License

