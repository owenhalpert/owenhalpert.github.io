#!/usr/bin/env python3
"""
One-time script to get a Spotify refresh token.

Usage:
  1. Create a Spotify app at https://developer.spotify.com/dashboard
  2. Add http://localhost:8888/callback as a Redirect URI in the app settings
  3. Run: python3 scripts/get-refresh-token.py
  4. Copy the printed refresh token into your Vercel environment variables
"""

import http.server
import urllib.parse
import urllib.request
import webbrowser
import base64
import json
import os

CLIENT_ID = input("Enter your Spotify Client ID: ").strip()
CLIENT_SECRET = input("Enter your Spotify Client Secret: ").strip()
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-currently-playing user-read-playback-state"

auth_url = (
    "https://accounts.spotify.com/authorize"
    f"?client_id={CLIENT_ID}"
    f"&response_type=code"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPE)}"
)

print("\nOpening Spotify login in your browser...")
webbrowser.open(auth_url)

code_holder = {}

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code_holder['code'] = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<html><body><h2>Got it! You can close this tab.</h2></body></html>")

    def log_message(self, format, *args):
        pass  # suppress request logs

server = http.server.HTTPServer(('localhost', 8888), CallbackHandler)
print("Waiting for Spotify callback...")
server.handle_request()

code = code_holder.get('code')
if not code:
    print("Error: no code received.")
    exit(1)

credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI,
}).encode()

req = urllib.request.Request(
    "https://accounts.spotify.com/api/token",
    data=data,
    headers={
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    method="POST",
)

with urllib.request.urlopen(req) as response:
    tokens = json.loads(response.read())

print("\n✓ Success!\n")
print(f"  Refresh token: {tokens['refresh_token']}")
print("\nAdd these to Vercel environment variables:")
print(f"  SPOTIFY_CLIENT_ID     = {CLIENT_ID}")
print(f"  SPOTIFY_CLIENT_SECRET = {CLIENT_SECRET}")
print(f"  SPOTIFY_REFRESH_TOKEN = {tokens['refresh_token']}")
