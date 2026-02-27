"""Start ngrok tunnel and keep it alive."""
import time
from pyngrok import ngrok

ngrok.set_auth_token("1ctMp8i95cv694TXidg3lvsdpRM_7QU4LgUhkNVzNkdaN6EhR")

# Kill any existing tunnels
ngrok.kill()
time.sleep(1)

tunnel = ngrok.connect(8001, bind_tls=True)
public_url = tunnel.public_url
print(f"NGROK_URL={public_url}", flush=True)
print(f"Webhook URL: {public_url}/api/whatsapp/webhook", flush=True)

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.kill()
