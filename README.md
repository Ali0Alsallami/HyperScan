# HyperScan v2.0
An advanced, portable web scanning and crawling tool for OSINT and penetration testing.

## Features
- Asynchronous crawling and directory scanning
- Extracts emails, JS files, API endpoints
- Vulnerability detection (e.g., exposed .env files)
- Proxy support, JSON/TXT output
- Cross-platform: Termux, Linux, Docker
- Resource-aware concurrency

## Installation
```bash
pkg install python git
pip install -r requirements.txt
git clone https://github.com/<your-username>/HyperScan.git
cd HyperScan
