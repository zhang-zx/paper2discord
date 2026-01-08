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

def send_discord_message(webhook_url, content, thread_name=None, thread_id=None):
    """
    Sends a message to Discord via Webhook.
    - If `thread_name` is provided, creates a new thread with that name and returns the thread_id.
    - If `thread_id` is provided, sends the message into that thread.
    """
    if not webhook_url:
        print("Error: Missing Discord Webhook URL.")
        return None

    chunks = smart_split(content)
    last_response_id = None

    for i, chunk in enumerate(chunks):
        if not chunk: continue
        
        data = {
            "content": chunk
        }
        
        # Only apply thread_name to the first chunk to create the thread
        if thread_name and i == 0:
            data["thread_name"] = thread_name
        
        # Prepare params
        params = {}
        if thread_id:
            params["thread_id"] = thread_id
        
        # If we are creating a thread, we need to wait for response to get ID
        if thread_name and i == 0:
            params["wait"] = "true"

        try:
            response = requests.post(webhook_url, json=data, params=params)
            response.raise_for_status()
            
            # If we created a thread, get the Thread ID.
            # When creating a thread via webhook, the response is the Message object.
            # The 'channel_id' of this message is the ID of the newly created thread.
            if thread_name and i == 0:
                try:
                    resp_json = response.json()
                    # print(f"DEBUG: Thread Creation Response: {resp_json}")
                    last_response_id = resp_json.get('channel_id')
                except:
                    pass
            
            # Rate limiting prevention
            time.sleep(1) 
        except requests.RequestException as e:
            print(f"Error sending to Discord: {e}")
            try:
                print(f"Discord API Response: {response.text}")
            except:
                pass
            
    return last_response_id

def send_markdown_report(webhook_url, text, thread_id=None):
    """
    Parses a markdown report with ## headers and sends each section as a distinct message.
    """
    if not webhook_url: return

    # Split by '## ' which indicates a new section
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
            # We don't support creating threads inside markdown report splitting
            # So just pass thread_id if it exists
            send_discord_message(webhook_url, section, thread_id=thread_id)
        else:
            send_discord_message(webhook_url, section, thread_id=thread_id)