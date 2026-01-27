# Changelog

All notable changes to NanoMan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.2] - 2026-01-27

### Added
- **Presets Tab**: New dedicated tab for auth presets and API templates
- **Auth Presets**: Quick setup for Bearer Token, Basic Auth, API Key authentication
- **API Templates**: Pre-configured templates for Microsoft Graph API, GitHub API, HTTPBin, ReqRes, JSONPlaceholder, and Localhost
- **Data Storage**: History now stored in user config directory (`~/.nanoman/`)

### Changed
- Version management centralized in `version.py`
- Default URL removed (empty with placeholder) - aligns with offline-first philosophy
- Tab bar reorganized: main tabs (blue) + special tabs (purple)
- All tab buttons unified to 110px width with centered text
- README updated with Presets documentation and Data Storage section

### Security
- Headers and request body are never persisted to history
- History file moved out of repository to prevent accidental commits

---

## [1.2.1] - 2026-01-25

### Added
- Nano Design System integration
- Color palette and fonts from `nano_theme.py`
- JSON syntax highlighting with Nano colors

### Changed
- UI styling aligned with Nano Product Family
- Version bump to 1.2.1

---

## [1.2.0] - 2026-01-24

### Added
- Request history persistence to `history.json`
- Load previous requests from history with one click
- Request counter in status bar

### Changed
- History tab now shows saved requests
- Performance limit for JSON highlighting (1000 lines max)

---

## [1.1.0] - 2026-01-23

### Added
- Custom headers support in dedicated Headers tab
- Request body tab for POST/PUT/PATCH payloads
- Tab-based interface for better organization

### Changed
- UI restructured with tabbed content area
- Improved error handling and status messages

---

## [1.0.0] - 2026-01-22

### Added
- Initial release
- HTTP methods: GET, POST, PUT, PATCH, DELETE
- JSON syntax highlighting for responses
- Threaded requests (non-blocking UI)
- URL validation (HTTP/HTTPS only)
- Dark theme with CustomTkinter
- Part of Nano Product Family

### Security
- Strict URL validation prevents XSS via javascript:, file:, data: URLs
- 10 second request timeout
