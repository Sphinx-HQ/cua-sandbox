import subprocess
import json
import sys
import re

import pyotp


def run_bw_command(command):
    """Run a Bitwarden CLI command and return its stdout output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()


def get_auth_data(client_id: str, client_secret: str, master_password: str):
    # Check login status first
    status_output = run_bw_command("bw status")
    status = json.loads(status_output)

    if status.get("status") == "unauthenticated":
        # Log in using API key
        print("Logging in to Bitwarden CLI...")
        run_bw_command(f"BW_CLIENTID={client_id} BW_CLIENTSECRET={client_secret} bw login --apikey")

        status_output = run_bw_command("bw status")
        status = json.loads(status_output)

    # Unlock the vault
    print("Unlocking the vault...")
    session_token_msg = run_bw_command(f"BW_PASSWORD='{master_password}' bw unlock --passwordenv BW_PASSWORD")
    # '\x1b[92mYour vault is now unlocked!\x1b[39m\n\nTo unlock your vault, set your session key to the `BW_SESSION` environment variable. ex:\n$ export BW_SESSION="EbOLvtfkfw/emlS4X00jwqNz7jeLLgOJqQ4JJSEcvy9BKlQSqVieUrF8DxhcTfBHeIzQ/jBn/zochl8+pyO8jw=="\n> $env:BW_SESSION="EbOLvtfkfw/emlS4X00jwqNz7jeLLgOJqQ4JJSEcvy9BKlQSqVieUrF8DxhcTfBHeIzQ/jBn/zochl8+pyO8jw=="\n\nYou can also pass the session key to any command with the `--session` option. ex:\n$ bw list items --session EbOLvtfkfw/emlS4X00jwqNz7jeLLgOJqQ4JJSEcvy9BKlQSqVieUrF8DxhcTfBHeIzQ/jBn/zochl8+pyO8jw=='
    # Look for the session token pattern in the output
    session_match = re.search(r'BW_SESSION="([^"]+)"', session_token_msg)
    session_token = session_match.group(1)

    print("Retrieving vault items...")
    # Retrieve all items in the vault as JSON.
    items_json = run_bw_command(f"bw list items --session {session_token}")
    items = json.loads(items_json)

    # Loop through each item and print login details if available.
    hubspot = [item for item in items if "Hubspot" in item["name"]][0]
    username = hubspot["login"]["username"]
    password = hubspot["login"]["password"]
    totp_secret = hubspot["login"]["totp"]
    totp_secret = totp_secret.replace(" ", "")

    totp = pyotp.TOTP(totp_secret)
    totp_code = totp.now()

    response = {
        "username": username,
        "password": password,
        "totp_code": totp_code,
    }

    print(json.dumps(response, indent=2))
    return response
