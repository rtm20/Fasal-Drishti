"""
FasalDrishti — ngrok tunnel helper.
Starts ngrok, detects the public URL, and optionally updates .env.

Usage:
    python scripts/start_ngrok.py
    python scripts/start_ngrok.py --update-env
"""

import subprocess
import sys
import time
import json
import os
import re


def get_ngrok_url():
    """Query the ngrok API for the current tunnel's public URL."""
    try:
        import urllib.request

        resp = urllib.request.urlopen("http://localhost:4040/api/tunnels")
        data = json.loads(resp.read().decode())
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "https":
                return tunnel["public_url"]
    except Exception:
        return None


def update_env_file(public_url: str):
    """Update PUBLIC_URL in backend/.env."""
    env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
    env_path = os.path.abspath(env_path)

    if not os.path.exists(env_path):
        print(f"  [!] .env not found at {env_path}")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "PUBLIC_URL=" in content:
        content = re.sub(r"PUBLIC_URL=.*", f"PUBLIC_URL={public_url}", content)
    else:
        content += f"\nPUBLIC_URL={public_url}\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [+] Updated PUBLIC_URL in {env_path}")


def main():
    update_env = "--update-env" in sys.argv

    print("=" * 55)
    print("  FasalDrishti — ngrok Tunnel Helper")
    print("=" * 55)
    print()

    # Check if ngrok is already running
    url = get_ngrok_url()
    if url:
        print(f"  [*] ngrok already running!")
        print(f"  [*] Public URL: {url}")
        print(f"  [*] Webhook:    {url}/api/whatsapp/webhook")
        if update_env:
            update_env_file(url)
        print()
        print("  Set this webhook URL in your Twilio/Meta console.")
        return

    # Start ngrok
    print("  [*] Starting ngrok tunnel on port 8000...")
    try:
        proc = subprocess.Popen(
            ["ngrok", "http", "8000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("  [!] ngrok not found. Install it:")
        print("      choco install ngrok     (Windows)")
        print("      brew install ngrok       (macOS)")
        print("      Download: https://ngrok.com/download")
        sys.exit(1)

    # Wait for tunnel to establish
    print("  [*] Waiting for tunnel to establish...", end="", flush=True)
    for _ in range(15):
        time.sleep(1)
        print(".", end="", flush=True)
        url = get_ngrok_url()
        if url:
            break

    print()

    if not url:
        print("  [!] Could not detect ngrok URL. Check http://localhost:4040")
        sys.exit(1)

    print()
    print(f"  ╔═══════════════════════════════════════════════════╗")
    print(f"  ║  ngrok tunnel active!                            ║")
    print(f"  ╠═══════════════════════════════════════════════════╣")
    print(f"  ║  Public URL:  {url:<38s}║")
    print(f"  ║  Webhook:     {url}/api/whatsapp/webhook")
    print(f"  ║  Dashboard:   http://localhost:4040               ║")
    print(f"  ╚═══════════════════════════════════════════════════╝")
    print()

    if update_env:
        update_env_file(url)

    print("  Next steps:")
    print("  1. Copy the webhook URL above")
    print("  2. Paste in Twilio WhatsApp Sandbox settings")
    print("     (WHEN A MESSAGE COMES IN → POST)")
    print("  3. Send 'hi' on WhatsApp to test!")
    print()
    print("  Press Ctrl+C to stop ngrok.")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\n  [*] ngrok stopped.")


if __name__ == "__main__":
    main()
