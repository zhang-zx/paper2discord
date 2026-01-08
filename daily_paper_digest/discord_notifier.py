import requests
import time

def smart_split(text, limit=1900):
    """
    Splits text into chunks strictly under 'limit' characters.
    Tries to split by double newlines (paragraphs) first, then single newlines.
    """
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first to preserve structure
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds limit
        if len(current_chunk) + len(paragraph) + 1 > limit:
            # If the current chunk is not empty, save it
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If the paragraph itself is huge (larger than limit), we must hard-split it
            if len(paragraph) > limit:
                # Fallback to hard slicing for massive single blocks
                sub_chunks = [paragraph[i:i+limit] for i in range(0, len(paragraph), limit)]
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1] + "\n"
            else:
                current_chunk = paragraph + "\n"
        else:
            current_chunk += paragraph + "\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def send_markdown_report(webhook_url, text):
    """
    Parses a markdown report with ## headers and sends each section as a distinct message.
    Prevents splitting sections mid-way unless they are huge.
    """
    if not webhook_url: return

    # Split by '## ' which indicates a new section
    # We use a lookahead or just manual splitting
    lines = text.split('\n')
    sections = []
    current_section = ""
    
    for line in lines:
        if line.strip().startswith("## "):
            if current_section.strip():
                sections.append(current_section.strip())
            current_section = line + "\n"
        else:
            current_section += line + "\n"
            
    if current_section.strip():
        sections.append(current_section.strip())
        
    # Send each section
    for section in sections:
        # If section is huge (>1900), fall back to smart_split
        if len(section) > 1900:
            sub_chunks = smart_split(section)
            for sub in sub_chunks:
                send_discord_message(webhook_url, sub)
        else:
            send_discord_message(webhook_url, section)

def send_discord_message(webhook_url, content):
    """
    Sends a message to Discord via Webhook.
    Uses smart splitting to preserve formatting.
    """
    if not webhook_url:
        print("Error: Missing Discord Webhook URL.")
        return

    chunks = smart_split(content)

    for chunk in chunks:
        if not chunk: continue
        
        data = {
            "content": chunk
        }
        try:
            response = requests.post(webhook_url, json=data)
            response.raise_for_status()
            # Rate limiting prevention (polite delay)
            time.sleep(1) 
        except requests.RequestException as e:
            print(f"Error sending to Discord: {e}")