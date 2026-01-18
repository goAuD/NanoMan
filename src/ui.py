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

logger = logging.getLogger(__name__)

# Nano Design System
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

VERSION = "1.2.0"

# Constants
MAX_HIGHLIGHT_LINES = 1000  # Performance limit for syntax highlighting
MAX_HISTORY_ITEMS = 100  # Max items to persist
HISTORY_FILE = Path(__file__).parent.parent / "history.json"

# Nano Design System Colors (consistent with NanoServer)
COLORS = {
    "success": "#4caf50",      # NanoServer green
    "danger": "#e74c3c",       # Error red
    "warning": "#e67e22",      # Warning orange
    "neutral": "#34495e",      # Neutral gray
    "primary": "#3498db",      # Blue primary
    "muted": "gray",           # Muted text
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
        
        # URL entry
        self.entry_url = ctk.CTkEntry(
            self.control_frame, 
            placeholder_text="Enter API URL (e.g., https://api.example.com/data)",
            height=40,
            font=("Consolas", 13)
        )
        self.entry_url.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_url.insert(0, "https://chseets.com/api/meta.json")
        
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
        tabs = [
            ("response", "Response"),
            ("body", "Request Body"),
            ("headers", "Headers"),
            ("history", "History")
        ]
        
        for i, (key, label) in enumerate(tabs):
            btn = ctk.CTkButton(
                self.tab_bar,
                text=label,
                width=120,
                height=32,
                font=("Roboto", 12),
                fg_color="#2c3e50" if key != "response" else "#3498db",
                hover_color="#34495e",
                corner_radius=8,
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
        self.txt_response.insert("0.0", "// Response will appear here\n// Press SEND or Enter to make a request\n\n// Try the chseets API:\n// https://chseets.com/api/meta.json\n// https://chseets.com/api/sheets/weiz.json")
    
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
        
        # Update button colors
        for key, btn in self.tab_buttons.items():
            if key == tab_key:
                btn.configure(fg_color="#3498db")
            else:
                btn.configure(fg_color="#2c3e50")
        
        # Hide all frames
        self.response_frame.grid_remove()
        self.body_frame.grid_remove()
        self.headers_frame.grid_remove()
        self.history_frame.grid_remove()
        
        # Show selected frame
        if tab_key == "response":
            self.response_frame.grid()
        elif tab_key == "body":
            self.body_frame.grid()
        elif tab_key == "headers":
            self.headers_frame.grid()
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
        """Add a request to history."""
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

