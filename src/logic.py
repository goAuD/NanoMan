"""
NanoMan - Logic Module
Business logic for API testing, URL validation, and request handling.
Part of the Nano Product Family.

Security Focus:
- Only HTTP/HTTPS URLs allowed (prevents XSS, javascript: exploits)
- Strict URL validation with regex
- Request timeout to prevent hanging
- Proper JSON parsing with error handling
"""

import requests
import json
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """
    Validate that URL is safe and properly formatted.
    Only HTTP and HTTPS protocols are allowed.
    
    Security: Prevents XSS via javascript:, ftp:, file:, data: URLs
    
    Note: Allows intranet hostnames without TLD (e.g., http://intranet/api)
    
    Args:
        url: The URL to validate
        
    Returns:
        True if URL is valid and safe, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Relaxed regex: allows http:// or https:// with various host formats
    # - Domain with TLD (example.com)
    # - Hostname without TLD (intranet, server1)
    # - localhost
    # - IPv4 addresses
    pattern = re.compile(
        r'^https?://'  # http:// or https:// ONLY
        r'(?:'
            r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?'  # Any hostname
            r'|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'  # or IPv4
        r')'
        r'(?::\d{1,5})?'  # Optional port
        r'(?:/[^\s]*)?$',  # Optional path
        re.IGNORECASE
    )
    
    return bool(pattern.match(url))


def format_json(text: str) -> str:
    """
    Format JSON string with pretty printing.
    
    Args:
        text: Raw JSON string
        
    Returns:
        Formatted JSON string, or original text if parsing fails
    """
    if not text:
        return text
    
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, indent=4, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return text


def parse_headers(headers_text: str) -> Dict[str, str]:
    """
    Parse headers from text format (key: value per line).
    
    Args:
        headers_text: Headers in text format
        
    Returns:
        Dictionary of headers
    """
    headers = {}
    if not headers_text or not headers_text.strip():
        return headers
    
    for line in headers_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    
    return headers


def send_api_request(
    method: str, 
    url: str, 
    payload: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Send an API request and return the result.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        url: Target URL
        payload: JSON payload for POST/PUT/PATCH
        headers: Optional request headers
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with response data or error information
    """
    # Security: Validate URL first
    if not validate_url(url):
        logger.warning(f"Invalid URL rejected: {url[:50]}...")
        return {
            "success": False,
            "error": "Invalid or unsafe URL. Only http:// and https:// are allowed."
        }
    
    # Parse JSON payload if provided
    json_data = None
    if payload and payload.strip():
        try:
            json_data = json.loads(payload)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in request body: {str(e)}"
            }
    
    # Send request
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=json_data,
            headers=headers or {},
            timeout=timeout
        )
        
        # Determine if response is JSON
        content_type = response.headers.get("Content-Type", "")
        is_json = "application/json" in content_type
        
        # Format response body
        body = response.text
        if is_json:
            body = format_json(body)
        
        return {
            "success": True,
            "status_code": response.status_code,
            "reason": response.reason,
            "elapsed_seconds": response.elapsed.total_seconds(),
            "headers": dict(response.headers),
            "body": body,
            "is_json": is_json
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Request timed out after {timeout} seconds"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "error": f"Connection failed: {str(e)}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
