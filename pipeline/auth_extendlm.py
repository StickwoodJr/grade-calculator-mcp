#!/usr/bin/env python3
"""
Robust OAuth Authenticator for ExtendLM MCP in Antigravity.

Supports:
1. Dual IPv4/IPv6 listening on port 63483 so 'localhost' never gives connection refused.
2. Direct paste: 'python3 pipeline/auth_extendlm.py --url "http://localhost:63483/callback?code=..."'
3. Interactive code / URL prompt if the browser cannot reach localhost.
4. Token saving to ~/.gemini/config/extendlm_token.json.
"""

import os
import sys
import json
import base64
import hashlib
import secrets
import argparse
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

TOKEN_PATH = os.path.expanduser("~/.gemini/config/extendlm_token.json")
PKCE_CACHE_PATH = os.path.expanduser("~/.gemini/config/.extendlm_pkce.json")

AUTH_URL = "https://api.extendlm.com/rest/v1/mcp/oauth/authorize"
TOKEN_URL = "https://api.extendlm.com/rest/v1/mcp/oauth/token"
CLIENT_ID = "https://claude.ai/oauth/claude-code-client-metadata"
REDIRECT_URI = "http://localhost:63483/callback"
SCOPE = "notebooks:read sources:read notes:read artifacts:read chat:read labels:read prompts:read folders:read tags:read library:read research:read exports:create exports:download notebooks:write sources:write notes:write chat:write labels:write prompts:write artifacts:create artifacts:write research:write tasks:read tasks:write folders:write tags:write library:write"

class DualStackServer(HTTPServer):
    address_family = socket.AF_INET6 if socket.has_ipv6 else socket.AF_INET

    def server_bind(self):
        if socket.has_ipv6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, OSError):
                pass
        super().server_bind()

received_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global received_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            received_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html><body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0F172A; color: white;">
                <h1 style="color: #10B981;">Authentication Successful!</h1>
                <p>ExtendLM MCP is now authenticated. You can close this tab and return to Antigravity.</p>
            </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"No code parameter found in callback.")

    def log_message(self, format, *args):
        pass

def get_or_create_pkce():
    if os.path.exists(PKCE_CACHE_PATH):
        try:
            with open(PKCE_CACHE_PATH, "r") as f:
                data = json.load(f)
                return data["verifier"], data["challenge"], data["state"]
        except Exception:
            pass

    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest()).decode('ascii').rstrip('=')
    state = secrets.token_urlsafe(16)
    os.makedirs(os.path.dirname(PKCE_CACHE_PATH), exist_ok=True)
    with open(PKCE_CACHE_PATH, "w") as f:
        json.dump({"verifier": verifier, "challenge": challenge, "state": state}, f)
    return verifier, challenge, state

def exchange_code_for_token(code: str, verifier: str):
    print(f"[*] Exchanging authorization code for Bearer token...")
    token_data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
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
            print(f"\n[✓] SUCCESS: Bearer token saved to {TOKEN_PATH}")
            if os.path.exists(PKCE_CACHE_PATH):
                os.remove(PKCE_CACHE_PATH)
            return tokens
    except urllib.error.HTTPError as e:
        print(f"[!] Token exchange failed ({e.code}): {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[!] Token exchange error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Authenticate ExtendLM MCP for Antigravity")
    parser.add_argument("--url", help="Pasted redirect URL from browser address bar")
    parser.add_argument("--code", help="Pasted authorization code")
    args = parser.parse_args()

    verifier, challenge, state = get_or_create_pkce()

    if args.code:
        exchange_code_for_token(args.code, verifier)
        return

    if args.url:
        parsed = urllib.parse.urlparse(args.url)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            exchange_code_for_token(params["code"][0], verifier)
            return
        else:
            print("[!] No 'code' parameter found in the provided URL.")
            return

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
    print("=" * 75)
    print("ExtendLM MCP Authentication for Antigravity")
    print("=" * 75)
    print("\n1. Please open or refresh this authorization link in your browser:\n")
    print(url)
    print("\n2. The local callback listener is active on port 63483 (IPv4 & IPv6).")
    print("   If your browser displays 'Connection Refused', simply COPY the URL from")
    print("   the address bar and paste it here, or run:")
    print("   python3 pipeline/auth_extendlm.py --url '<paste-copied-url>'")
    print("=" * 75)

    host = "::" if socket.has_ipv6 else "0.0.0.0"
    try:
        server = DualStackServer((host, 63483), OAuthHandler)
    except Exception:
        server = HTTPServer(("0.0.0.0", 63483), OAuthHandler)

    print(f"\nListening on {host}:63483 ...")
    while not received_code:
        server.handle_request()

    server.server_close()
    if received_code:
        exchange_code_for_token(received_code, verifier)

if __name__ == "__main__":
    main()
