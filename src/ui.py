"""
NanoMan - UI Module
CustomTkinter user interface for API testing.
Part of the Nano Product Family.
"""

import customtkinter as ctk
import threading
import logging
import json
import re
import os
from datetime import datetime
from pathlib import Path

from src.logic import validate_url, send_api_request, format_json, parse_headers
from src.presets import (
    AUTH_PRESETS, API_TEMPLATES, 
    get_auth_preset_names, get_api_template_names,
    get_auth_preset_by_name, get_api_template_by_name,
)
from version import VERSION

# Import Nano Design System
try:
    from nano_theme import NANO_COLORS, NANO_FONTS, apply_nano_theme
    apply_nano_theme()
except ImportError:
    # Fallback if nano_theme not available
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    NANO_COLORS = {}
    NANO_FONTS = {}

logger = logging.getLogger(__name__)

# Constants
MAX_HIGHLIGHT_LINES = 1000  # Performance limit for syntax highlighting
MAX_HISTORY_ITEMS = 100  # Max items to persist


def get_config_dir() -> Path:
    """Get user config directory (~/.nanoman/)."""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('USERPROFILE', Path.home())) / '.nanoman'
    else:  # Linux/Mac
        config_dir = Path.home() / '.nanoman'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


HISTORY_FILE = get_config_dir() / "history.json"

# Nano Design System Colors (from nano_theme.py)
COLORS = {
    "success": NANO_COLORS.get("accent_green", "#4caf50"),
    "danger": NANO_COLORS.get("accent_red", "#e74c3c"),
    "warning": NANO_COLORS.get("accent_orange", "#e67e22"),
    "neutral": NANO_COLORS.get("neutral", "#34495e"),
    "primary": NANO_COLORS.get("primary", "#3498db"),
    "muted": NANO_COLORS.get("text_muted", "gray"),
    "link": NANO_COLORS.get("text_link", "#00CED1"),
    "special": NANO_COLORS.get("accent_purple", "#9b59b6"),  # For Presets/History tabs
}


class NanoManApp(ctk.CTk):
    """Main application window for NanoMan API client."""
    
    def __init__(self):
        super().__init__()
        
        # Window settings
        self.title(f"NanoMan v{VERSION} - Offline API Client")
        self.geometry("1000x800")
        self.minsize(900, 700)
        
        # History storage
        self.history = []
        self.load_history()  # Load from file
        
        # Current tab
        self.current_tab = "response"
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Content area expands
        
        self.create_widgets()
        
        # Save history on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        logger.info(f"NanoMan v{VERSION} started")
    
    def create_widgets(self):
        """Create all UI widgets."""
        
        # 1. Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        
        self.lbl_title = ctk.CTkLabel(
            self.header_frame, 
            text="NanoMan", 
            font=("Roboto", 24, "bold")
        )
        self.lbl_title.pack(side="left")
        
        self.lbl_subtitle = ctk.CTkLabel(
            self.header_frame, 
            text="No Cloud. No Bloat. Just Requests.",
            text_color="gray"
        )
        self.lbl_subtitle.pack(side="left", padx=15)
        
        self.lbl_family = ctk.CTkLabel(
            self.header_frame, 
            text="Nano Product Family",
            font=("Roboto", 10),
            text_color="#00CED1"
        )
        self.lbl_family.pack(side="right")
        
        # 2. Control bar (Method + URL + Send)
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1)
        
        # Method selector
        self.method_var = ctk.StringVar(value="GET")
        self.opt_method = ctk.CTkOptionMenu(
            self.control_frame, 
            values=["GET", "POST", "PUT", "PATCH", "DELETE"],
            variable=self.method_var, 
            width=100, 
            fg_color="#2c3e50",
            button_color="#34495e",
            button_hover_color="#3d566e"
        )
        self.opt_method.grid(row=0, column=0, padx=10, pady=10)
        
        # URL entry (empty by default - offline first)
        self.entry_url = ctk.CTkEntry(
            self.control_frame, 
            placeholder_text="Enter API URL (e.g., http://localhost:8080/api)",
            height=40,
            font=("Consolas", 13)
        )
        self.entry_url.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # No default value - placeholder is sufficient
        
        # Bind Enter key to send
        self.entry_url.bind("<Return>", lambda e: self.send_request_thread())
        
        # Send button
        self.btn_send = ctk.CTkButton(
            self.control_frame, 
            text="SEND",
            width=100,
            height=40,
            fg_color="#27ae60", 
            hover_color="#2ecc71",
            font=("Roboto", 14, "bold"),
            command=self.send_request_thread
        )
        self.btn_send.grid(row=0, column=2, padx=5, pady=10)
        
        # Clear button
        self.btn_clear = ctk.CTkButton(
            self.control_frame, 
            text="CLEAR",
            width=80,
            height=40,
            fg_color="#7f8c8d", 
            hover_color="#95a5a6",
            font=("Roboto", 12),
            command=self.clear_response
        )
        self.btn_clear.grid(row=0, column=3, padx=5, pady=10)
        
        # 3. Custom Tab Bar (separate frame above content)
        self.tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_bar.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        self.tab_buttons = {}
        
        # Main tabs (blue theme)
        main_tabs = [
            ("response", "Response"),
            ("body", "Request Body"),
            ("headers", "Headers"),
        ]
        
        # Special tabs (purple theme - logically separate)
        special_tabs = [
            ("presets", "Presets"),
            ("history", "History"),
        ]
        
        for key, label in main_tabs:
            btn = ctk.CTkButton(
                self.tab_bar,
                text=label,
                width=110,
                height=32,
                font=("Roboto", 12),
                fg_color="#3498db" if key == "response" else "#2c3e50",
                hover_color="#34495e",
                corner_radius=8,
                anchor="center",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(side="left", padx=3)
            self.tab_buttons[key] = btn
        
        # Spacer to push special tabs to the right
        spacer = ctk.CTkLabel(self.tab_bar, text="", width=20)
        spacer.pack(side="left", expand=True)
        
        for key, label in special_tabs:
            btn = ctk.CTkButton(
                self.tab_bar,
                text=label,
                width=110,
                height=32,
                font=("Roboto", 12),
                fg_color=COLORS["special"],  # Purple for special tabs
                hover_color="#8e44ad",
                corner_radius=8,
                anchor="center",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.pack(side="left", padx=3)
            self.tab_buttons[key] = btn
        
        # 4. Content Area (single frame, content swapped)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create all content widgets (hidden initially except response)
        self._create_response_content()
        self._create_body_content()
        self._create_headers_content()
        self._create_presets_content()
        self._create_history_content()
        
        # 5. Status bar
        self.status_frame = ctk.CTkFrame(self, height=35, fg_color="transparent")
        self.status_frame.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(
            self.status_frame, 
            text="Ready. Enter a URL and press SEND.",
            anchor="w",
            font=("Roboto", 12)
        )
        self.lbl_status.pack(side="left", fill="x")
        
        # Request count label
        self.lbl_count = ctk.CTkLabel(
            self.status_frame, 
            text="Requests: 0",
            anchor="e",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.lbl_count.pack(side="right")
    
    def _create_response_content(self):
        """Create response tab content."""
        self.response_frame = ctk.CTkFrame(self.content_frame)
        self.response_frame.grid(row=0, column=0, sticky="nsew")
        self.response_frame.grid_columnconfigure(0, weight=1)
        self.response_frame.grid_rowconfigure(0, weight=1)
        
        self.txt_response = ctk.CTkTextbox(
            self.response_frame, 
            font=("Consolas", 13),
            wrap="word"
        )
        self.txt_response.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.txt_response.insert("0.0", "// Response will appear here\n// Press SEND or Enter to make a request\n\n// Quick start:\n// 1. Enter a URL or use Presets tab for templates\n// 2. Select HTTP method\n// 3. Press SEND or Enter\n\n// Try these test APIs:\n// https://httpbin.org/get\n// https://jsonplaceholder.typicode.com/posts/1")
    
    def _create_body_content(self):
        """Create request body tab content."""
        self.body_frame = ctk.CTkFrame(self.content_frame)
        self.body_frame.grid(row=0, column=0, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=1)
        self.body_frame.grid_rowconfigure(0, weight=1)
        
        self.txt_body = ctk.CTkTextbox(
            self.body_frame, 
            font=("Consolas", 13)
        )
        self.txt_body.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.txt_body.insert("0.0", '{\n    "key": "value"\n}')
        
        self.body_frame.grid_remove()  # Hide initially
    
    def _create_headers_content(self):
        """Create headers tab content."""
        self.headers_frame = ctk.CTkFrame(self.content_frame)
        self.headers_frame.grid(row=0, column=0, sticky="nsew")
        self.headers_frame.grid_columnconfigure(0, weight=1)
        self.headers_frame.grid_rowconfigure(0, weight=1)
        
        self.txt_headers = ctk.CTkTextbox(
            self.headers_frame, 
            font=("Consolas", 13)
        )
        self.txt_headers.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.txt_headers.insert("0.0", "Content-Type: application/json")
        
        self.headers_frame.grid_remove()  # Hide initially
    
    def _create_presets_content(self):
        """Create presets tab content with auth presets and API templates."""
        self.presets_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.presets_frame.grid(row=0, column=0, sticky="nsew")
        self.presets_frame.grid_columnconfigure(0, weight=1)
        self.presets_frame.grid_columnconfigure(1, weight=1)
        
        # Left side: Auth Presets
        auth_section = ctk.CTkFrame(self.presets_frame)
        auth_section.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(
            auth_section,
            text="Auth Presets",
            font=("Roboto", 14, "bold"),
            text_color=COLORS["special"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            auth_section,
            text="Select an auth method to apply headers",
            font=("Roboto", 11),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        self.auth_preset_var = ctk.StringVar(value="No Auth")
        self.auth_dropdown = ctk.CTkOptionMenu(
            auth_section,
            values=get_auth_preset_names(),
            variable=self.auth_preset_var,
            width=200,
            fg_color=COLORS["special"],
            button_color="#8e44ad",
            button_hover_color="#7d3c98",
            command=self._apply_auth_preset
        )
        self.auth_dropdown.pack(pady=5)
        
        self.auth_desc_label = ctk.CTkLabel(
            auth_section,
            text="No authentication required",
            font=("Roboto", 10),
            text_color="gray",
            wraplength=250
        )
        self.auth_desc_label.pack(pady=(5, 10))
        
        # Right side: API Templates
        template_section = ctk.CTkFrame(self.presets_frame)
        template_section.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(
            template_section,
            text="API Templates",
            font=("Roboto", 14, "bold"),
            text_color=COLORS["special"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            template_section,
            text="Click to load template URL and auth",
            font=("Roboto", 11),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Template buttons
        for name in get_api_template_names():
            template = get_api_template_by_name(name)
            btn = ctk.CTkButton(
                template_section,
                text=name,
                width=220,
                height=35,
                font=("Roboto", 11),
                fg_color="#2c3e50",
                hover_color="#34495e",
                anchor="center",
                command=lambda t=template: self._apply_api_template(t)
            )
            btn.pack(pady=2, padx=10)
        
        # Example endpoints section (below templates)
        self.template_examples_frame = ctk.CTkFrame(self.presets_frame)
        self.template_examples_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)
        
        self.template_examples_label = ctk.CTkLabel(
            self.template_examples_frame,
            text="Select a template to see example endpoints",
            font=("Roboto", 11),
            text_color="gray"
        )
        self.template_examples_label.pack(pady=10)
        
        self.presets_frame.grid_remove()  # Hide initially
    
    def _apply_auth_preset(self, preset_name: str):
        """Apply selected auth preset to headers."""
        preset = get_auth_preset_by_name(preset_name)
        if preset and preset.get("headers"):
            # Get current headers
            current = self.txt_headers.get("0.0", "end").strip()
            new_headers = []
            
            # Parse existing headers, remove Authorization if present
            for line in current.split('\n'):
                if ':' in line:
                    key = line.split(':', 1)[0].strip().lower()
                    if key not in ('authorization', 'x-api-key'):
                        new_headers.append(line)
            
            # Add preset headers
            for key, value in preset["headers"].items():
                new_headers.append(f"{key}: {value}")
            
            # Update headers textbox
            self.txt_headers.delete("0.0", "end")
            self.txt_headers.insert("0.0", '\n'.join(new_headers))
            
            # Update description
            desc = preset.get("description", "")
            if preset.get("docs"):
                desc += f"\nDocs: {preset['docs']}"
            self.auth_desc_label.configure(text=desc)
            
            self.lbl_status.configure(
                text=f"Applied auth preset: {preset_name}",
                text_color=COLORS["special"]
            )
        else:
            self.auth_desc_label.configure(text="No authentication required")
    
    def _apply_api_template(self, template: dict):
        """Apply API template to URL, method, and optionally auth."""
        base_url = template.get("base_url", "")
        
        # Set URL to first example or base URL
        examples = template.get("examples", [])
        if examples:
            first_example = examples[0]
            url = base_url + first_example.get("path", "")
            method = first_example.get("method", "GET")
        else:
            url = base_url
            method = "GET"
        
        # Update URL
        self.entry_url.delete(0, "end")
        self.entry_url.insert(0, url)
        
        # Update method
        self.method_var.set(method)
        
        # Apply auth preset if specified
        auth_key = template.get("auth", "none")
        if auth_key in AUTH_PRESETS:
            preset = AUTH_PRESETS[auth_key]
            self.auth_preset_var.set(preset["name"])
            self._apply_auth_preset(preset["name"])
        
        # Update examples display
        self._show_template_examples(template)
        
        self.lbl_status.configure(
            text=f"Loaded template: {template.get('name', 'Unknown')}",
            text_color=COLORS["special"]
        )
    
    def _show_template_examples(self, template: dict):
        """Show example endpoints for selected template."""
        # Clear existing content
        for widget in self.template_examples_frame.winfo_children():
            widget.destroy()
        
        # Header
        ctk.CTkLabel(
            self.template_examples_frame,
            text=f"{template.get('name', 'API')} - Example Endpoints",
            font=("Roboto", 12, "bold"),
            text_color=COLORS["link"]
        ).pack(pady=(10, 5))
        
        if template.get("docs"):
            ctk.CTkLabel(
                self.template_examples_frame,
                text=f"Docs: {template['docs']}",
                font=("Roboto", 10),
                text_color="gray"
            ).pack()
        
        # Example buttons
        examples = template.get("examples", [])
        for example in examples:
            btn_frame = ctk.CTkFrame(self.template_examples_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)
            
            method = example.get("method", "GET")
            path = example.get("path", "/")
            desc = example.get("desc", "")
            
            # Method badge color
            method_color = {
                "GET": COLORS["primary"],
                "POST": COLORS["success"],
                "PUT": COLORS["warning"],
                "PATCH": COLORS["warning"],
                "DELETE": COLORS["danger"],
            }.get(method, COLORS["neutral"])
            
            ctk.CTkLabel(
                btn_frame,
                text=method,
                font=("Consolas", 10, "bold"),
                text_color=method_color,
                width=50
            ).pack(side="left")
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"{path}  -  {desc}",
                font=("Consolas", 10),
                fg_color="transparent",
                hover_color="#34495e",
                text_color="white",
                anchor="w",
                command=lambda t=template, e=example: self._load_example(t, e)
            )
            btn.pack(side="left", fill="x", expand=True)
    
    def _load_example(self, template: dict, example: dict):
        """Load a specific example endpoint."""
        base_url = template.get("base_url", "")
        path = example.get("path", "")
        method = example.get("method", "GET")
        
        self.entry_url.delete(0, "end")
        self.entry_url.insert(0, base_url + path)
        self.method_var.set(method)
        
        self.switch_tab("response")
        self.lbl_status.configure(
            text=f"Loaded: {method} {path}",
            text_color=COLORS["primary"]
        )

    
    def _create_history_content(self):
        """Create history tab content."""
        self.history_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.history_frame.grid(row=0, column=0, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_history_empty = ctk.CTkLabel(
            self.history_frame,
            text="No requests yet. Send a request to see history.",
            text_color="gray"
        )
        self.lbl_history_empty.grid(row=0, column=0, pady=20)
        
        self.history_frame.grid_remove()  # Hide initially
    
    def switch_tab(self, tab_key: str):
        """Switch between tabs."""
        self.current_tab = tab_key
        
        # Define which tabs are "special" (purple theme)
        special_tabs = {"presets", "history"}
        main_tabs = {"response", "body", "headers"}
        
        # Update button colors
        for key, btn in self.tab_buttons.items():
            if key == tab_key:
                # Active tab gets highlighted
                if key in special_tabs:
                    btn.configure(fg_color="#8e44ad")  # Darker purple for active
                else:
                    btn.configure(fg_color="#3498db")  # Blue for active main tabs
            else:
                # Inactive tabs
                if key in special_tabs:
                    btn.configure(fg_color=COLORS["special"])  # Purple for special
                else:
                    btn.configure(fg_color="#2c3e50")  # Gray for main tabs
        
        # Hide all frames
        self.response_frame.grid_remove()
        self.body_frame.grid_remove()
        self.headers_frame.grid_remove()
        self.presets_frame.grid_remove()
        self.history_frame.grid_remove()
        
        # Show selected frame
        if tab_key == "response":
            self.response_frame.grid()
        elif tab_key == "body":
            self.body_frame.grid()
        elif tab_key == "headers":
            self.headers_frame.grid()
        elif tab_key == "presets":
            self.presets_frame.grid()
        elif tab_key == "history":
            self.history_frame.grid()
    
    def apply_json_highlighting(self, textbox: ctk.CTkTextbox, content: str):
        """Apply basic JSON syntax highlighting with performance limit."""
        textbox.delete("0.0", "end")
        textbox.insert("0.0", content)
        
        lines = content.split('\n')
        
        # Performance limit: skip highlighting for large JSON
        if len(lines) > MAX_HIGHLIGHT_LINES:
            logger.info(f"Skipping highlighting: {len(lines)} lines exceeds limit of {MAX_HIGHLIGHT_LINES}")
            return
        
        # Define tags (colors - aligned with Nano Design System)
        textbox._textbox.tag_configure("key", foreground=COLORS["warning"])    # Orange for keys
        textbox._textbox.tag_configure("string", foreground=COLORS["success"]) # Green for strings  
        textbox._textbox.tag_configure("number", foreground=COLORS["primary"]) # Blue for numbers
        textbox._textbox.tag_configure("boolean", foreground=COLORS["danger"]) # Red for booleans
        textbox._textbox.tag_configure("null", foreground="#9b59b6")           # Purple for null
        
        # Apply highlighting
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Keys (before colon)
            for match in re.finditer(r'"([^"]+)"\s*:', line):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()-1}"
                textbox._textbox.tag_add("key", start, end)
            
            # String values (after colon)
            for match in re.finditer(r':\s*"([^"]*)"', line):
                start = f"{line_num}.{match.start() + len(match.group(0)) - len(match.group(1)) - 1}"
                end = f"{line_num}.{match.end()}"
                textbox._textbox.tag_add("string", start, end)
            
            # Numbers
            for match in re.finditer(r':\s*(-?\d+\.?\d*)', line):
                start = f"{line_num}.{match.start(1)}"
                end = f"{line_num}.{match.end(1)}"
                textbox._textbox.tag_add("number", start, end)
            
            # Booleans
            for match in re.finditer(r'\b(true|false)\b', line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                textbox._textbox.tag_add("boolean", start, end)
            
            # Null
            for match in re.finditer(r'\bnull\b', line, re.IGNORECASE):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                textbox._textbox.tag_add("null", start, end)
    
    def clear_response(self):
        """Clear the response text."""
        self.txt_response.delete("0.0", "end")
        self.txt_response.insert("0.0", "// Cleared")
        self.lbl_status.configure(text="Response cleared.", text_color="gray")
    
    def add_to_history(self, method: str, url: str, status_code: int, elapsed: float):
        """
        Add a request to history.
        
        Security Note: Only method, URL, status, elapsed time, and timestamp are saved.
        Headers and request body are intentionally NOT persisted to prevent
        leaking sensitive data (Authorization tokens, API keys, etc.).
        """
        # Remove empty label if exists
        if hasattr(self, 'lbl_history_empty') and self.lbl_history_empty.winfo_exists():
            self.lbl_history_empty.destroy()
        
        # Add to list
        self.history.append({
            "method": method,
            "url": url,
            "status": status_code,
            "elapsed": elapsed,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        # Create history item
        row = len(self.history) - 1
        
        # Color based on status
        if 200 <= status_code < 300:
            color = "#27ae60"
        elif 300 <= status_code < 400:
            color = "#f39c12"
        else:
            color = "#e74c3c"
        
        item_frame = ctk.CTkFrame(self.history_frame, fg_color="#2a2d2e")
        item_frame.grid(row=row, column=0, sticky="ew", pady=2)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Method badge
        lbl_method = ctk.CTkLabel(
            item_frame,
            text=method,
            width=60,
            font=("Consolas", 11, "bold"),
            fg_color="#34495e",
            corner_radius=4
        )
        lbl_method.grid(row=0, column=0, padx=5, pady=5)
        
        # URL (truncated)
        display_url = url[:60] + "..." if len(url) > 60 else url
        lbl_url = ctk.CTkLabel(
            item_frame,
            text=display_url,
            font=("Consolas", 11),
            anchor="w"
        )
        lbl_url.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Status
        lbl_status = ctk.CTkLabel(
            item_frame,
            text=str(status_code),
            width=50,
            font=("Consolas", 11, "bold"),
            text_color=color
        )
        lbl_status.grid(row=0, column=2, padx=5, pady=5)
        
        # Time
        lbl_time = ctk.CTkLabel(
            item_frame,
            text=f"{elapsed:.2f}s",
            width=60,
            font=("Consolas", 10),
            text_color="gray"
        )
        lbl_time.grid(row=0, column=3, padx=5, pady=5)
        
        # Load button
        btn_load = ctk.CTkButton(
            item_frame,
            text="Load",
            width=50,
            height=25,
            font=("Roboto", 10),
            fg_color="#3498db",
            hover_color="#2980b9",
            command=lambda u=url, m=method: self.load_from_history(m, u)
        )
        btn_load.grid(row=0, column=4, padx=5, pady=5)
        
        # Update count
        self.lbl_count.configure(text=f"Requests: {len(self.history)}")
    
    def load_from_history(self, method: str, url: str):
        """Load a request from history."""
        self.method_var.set(method)
        self.entry_url.delete(0, "end")
        self.entry_url.insert(0, url)
        self.switch_tab("response")
        self.lbl_status.configure(text=f"Loaded from history: {method} {url[:50]}...", text_color="#3498db")
    
    def send_request_thread(self):
        """Start request in a separate thread to avoid UI freeze."""
        self.lbl_status.configure(text="Sending request...", text_color="orange")
        self.btn_send.configure(state="disabled", text="...")
        threading.Thread(target=self._execute_request, daemon=True).start()
    
    def _execute_request(self):
        """Execute the API request (runs in background thread)."""
        method = self.method_var.get()
        url = self.entry_url.get().strip()
        payload = self.txt_body.get("0.0", "end").strip()
        headers_text = self.txt_headers.get("0.0", "end").strip()
        
        # Parse headers
        headers = parse_headers(headers_text)
        
        # Allow body for all methods (ElasticSearch uses GET with body)
        # Trust the developer to know what they're doing
        
        # Make request
        result = send_api_request(method, url, payload, headers)
        
        # Update UI (thread-safe via after)
        self.after(0, lambda: self._update_ui(result, method, url))
    
    def _update_ui(self, result: dict, method: str, url: str):
        """Update UI with request result."""
        self.btn_send.configure(state="normal", text="SEND")
        
        if result.get("success"):
            status_code = result["status_code"]
            reason = result["reason"]
            elapsed = result["elapsed_seconds"]
            is_json = result.get("is_json", False)
            
            # Color based on status
            if 200 <= status_code < 300:
                color = "#27ae60"  # Green
            elif 300 <= status_code < 400:
                color = "#f39c12"  # Orange
            else:
                color = "#e74c3c"  # Red
            
            self.lbl_status.configure(
                text=f"Status: {status_code} {reason} | Time: {elapsed:.3f}s",
                text_color=color
            )
            
            # Show response with syntax highlighting if JSON
            if is_json:
                self.apply_json_highlighting(self.txt_response, result["body"])
            else:
                self.txt_response.delete("0.0", "end")
                self.txt_response.insert("0.0", result["body"])
            
            # Add to history
            self.add_to_history(method, url, status_code, elapsed)
            
            # Switch to response tab
            self.switch_tab("response")
        else:
            # Error
            self.lbl_status.configure(
                text=f"Error: {result['error'][:80]}...",
                text_color="#e74c3c"
            )
            self.txt_response.delete("0.0", "end")
            self.txt_response.insert("0.0", f"Error:\n{result['error']}")
            self.switch_tab("response")
    
    def load_history(self):
        """Load history from JSON file."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])[-MAX_HISTORY_ITEMS:]
                    logger.info(f"Loaded {len(self.history)} history items")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load history: {e}")
            self.history = []
    
    def save_history(self):
        """Save history to JSON file."""
        try:
            # Keep only last MAX_HISTORY_ITEMS
            history_to_save = self.history[-MAX_HISTORY_ITEMS:]
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({'history': history_to_save}, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(history_to_save)} history items")
        except IOError as e:
            logger.error(f"Could not save history: {e}")
    
    def on_close(self):
        """Handle window close event."""
        self.save_history()
        self.destroy()


def main():
    """Application entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app = NanoManApp()
    app.mainloop()


if __name__ == "__main__":
    main()

