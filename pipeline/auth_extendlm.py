#!/usr/bin/env python3
"""
OAuth Authenticator for ExtendLM MCP in Antigravity.

Performs OAuth 2.0 PKCE flow with ExtendLM, retrieves the Bearer access token,
and stores it in ~/.gemini/config/extendlm_token.json for Antigravity.
"""

import os
import sys
import json
import base64
import hashlib
import secrets
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import webbrowser

TOKEN_PATH = os.path.expanduser("~/.gemini/config/extendlm_token.json")
AUTH_URL = "https://api.extendlm.com/rest/v1/mcp/oauth/authorize"
TOKEN_URL = "https://api.extendlm.com/rest/v1/mcp/oauth/token"
CLIENT_ID = "https://claude.ai/oauth/claude-code-client-metadata"
REDIRECT_URI = "http://localhost:63483/callback"
SCOPE = "notebooks:read sources:read notes:read artifacts:read chat:read labels:read prompts:read folders:read tags:read library:read research:read exports:create exports:download notebooks:write sources:write notes:write chat:write labels:write prompts:write artifacts:create artifacts:write research:write tasks:read tasks:write folders:write tags:write library:write"

auth_code = None
server_done = threading.Event()

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication Successful!</h1><p>You can close this tab and return to Antigravity.</p>")
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication Failed</h1><p>No authorization code received.</p>")
        server_done.set()

    def log_message(self, format, *args):
        pass

def get_pkce_challenge():
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest()).decode('ascii').rstrip('=')
    return verifier, challenge

def authenticate():
    verifier, challenge = get_pkce_challenge()
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": SCOPE,
        "resource": "https://mcp.extendlm.com/mcp"
    }

    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print("=" * 70)
    print("ExtendLM MCP Authentication for Antigravity")
    print("=" * 70)
    print("\nPlease open the following URL in your Chrome browser (where ExtendLM is active):\n")
    print(url)
    print("\nWaiting for browser authorization callback on http://localhost:63483/callback ...")

    # Start local listener on port 63483
    server = HTTPServer(("localhost", 63483), OAuthHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()

    # Try opening browser automatically if possible
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # Wait up to 180 seconds
    server_done.wait(timeout=180)
    server.server_close()

    global auth_code
    if not auth_code:
        print("[!] No authorization code received (timeout or cancelled).")
        return None

    print(f"[✓] Received authorization code. Exchanging for Bearer access token...")
    token_data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier
    }).encode("utf-8")

    req = urllib.request.Request(TOKEN_URL, data=token_data, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    try:
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as f:
                json.dump(tokens, f, indent=2)
            print(f"[✓] Token successfully saved to: {TOKEN_PATH}")
            return tokens
    except Exception as e:
        print(f"[!] Token exchange failed: {e}")
        return None

if __name__ == "__main__":
    authenticate()
