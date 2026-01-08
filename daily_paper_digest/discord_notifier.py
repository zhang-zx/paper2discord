import requests
import json
import time

def send_discord_message(webhook_url, content):
    """
    Sends a message to Discord via Webhook.
    Splits long messages if necessary (Discord limit is 2000 chars).
    """
    if not webhook_url:
        print("Error: Missing Discord Webhook URL.")
        return

    # Split content into chunks of ~1900 chars to be safe
    chunk_size = 1900
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    for chunk in chunks:
        data = {
            "content": chunk
        }
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            # Rate limiting prevention
            time.sleep(1)
        except requests.RequestException as e:
            print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    # Test
    # url = "YOUR_WEBHOOK_URL"
    # send_discord_message(url, "Test message from Daily Paper Digest.")
    pass
