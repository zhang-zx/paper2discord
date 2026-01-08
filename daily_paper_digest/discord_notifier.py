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

def send_discord_message(webhook_url, content, thread_name=None, thread_id=None, image_file=None, image_filename="illustration.png"):
    """
    Sends a message to Discord via Webhook.
    - If `thread_name` is provided, creates a new thread with that name and returns the thread_id.
    - If `thread_id` is provided, sends the message into that thread.
    - If `image_file` (bytes or file-like) is provided, sends it as an attachment.
    """
    if not webhook_url:
        print("Error: Missing Discord Webhook URL.")
        return None

    chunks = smart_split(content)
    last_response_id = None

    # If there's an image, we usually send it with the LAST chunk or a separate message if text is empty?
    # Or send it with the first chunk?
    # Let's send it with the LAST chunk to appear at the bottom, OR if text is short, with the only chunk.
    # If text is long and split, sending with the last chunk makes sense.
    
    # However, creating a thread MUST happen on the first chunk.
    # If we have an image, we can send it with the first chunk too.
    
    for i, chunk in enumerate(chunks):
        if not chunk: continue
        
        data = {
            "content": chunk
        }
        files = None
        
        # Attach image to the LAST chunk to avoid it being buried if we split?
        # Actually, if we are creating a thread, we might want the image in the starter message.
        # But `thread_name` requires the message to be the starter.
        # Sending a file in the starter message is fine.
        
        # Let's attach to the LAST chunk for now, unless there's only 1 chunk.
        if image_file and i == len(chunks) - 1:
            # seek(0) just in case
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            files = {
                "file": (image_filename, image_file)
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

        # Retry loop for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if files:
                    # requests.post with 'files' automatically sets multipart/form-data
                    # We shouldn't set 'json' parameter then. We must use 'data' for payload fields.
                    # Discord expects 'payload_json' string or individual fields.
                    # Simplest is passing 'content' in data.
                    # Thread params still go in query string? No, thread_name goes in body.
                    
                    # Construct form data
                    form_data = {"content": data["content"]}
                    if "thread_name" in data:
                        form_data["thread_name"] = data["thread_name"]
                        
                    response = requests.post(webhook_url, data=form_data, files=files, params=params)
                else:
                    response = requests.post(webhook_url, json=data, params=params)
                
                if response.status_code == 429:
                    try:
                        retry_after = response.json().get('retry_after', 1)
                    except:
                        retry_after = 1
                    print(f"Rate limited. Waiting {retry_after}s...")
                    time.sleep(retry_after + 0.1)
                    continue # Retry
                
                response.raise_for_status()
                
                # If we created a thread, get its ID (which is the message ID or channel_id)
                # For Forum Channels, the response 'id' is the thread ID.
                # For Text Channels (if supported), 'id' is the message ID.
                # But typically 'id' of the response message object IS the thread ID for forum threads.
                if thread_name and i == 0:
                    try:
                        resp_json = response.json()
                        last_response_id = resp_json.get('id') 
                        # In forum channels, the created post's ID is the thread ID.
                    except:
                        pass
                
                # Successful, break retry loop
                break
                
            except requests.RequestException as e:
                print(f"Error sending to Discord: {e}")
                try:
                    print(f"Discord API Response: {response.text}")
                except:
                    pass
                # Don't break immediately on network errors, maybe retry? 
                # For now, just break to avoid infinite loops if it's a hard error.
                if response.status_code != 429:
                    break
        
        # Rate limiting prevention (polite delay between chunks)
        time.sleep(1)
            
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