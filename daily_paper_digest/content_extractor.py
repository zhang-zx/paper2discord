import requests
import io
from pypdf import PdfReader

def extract_text_from_pdf(pdf_url):
    """
    Downloads a PDF from the given URL and extracts its text content.
    Returns the extracted text as a string.
    """
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        
        # Load PDF from memory
        file_obj = io.BytesIO(response.content)
        reader = PdfReader(file_obj)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_url}: {e}")
        return None

if __name__ == "__main__":
    # Test with a known ArXiv PDF (random recent one or from scraper)
    # Example: Attention Is All You Need (1706.03762)
    url = "https://arxiv.org/pdf/1706.03762.pdf"
    print(f"Downloading and extracting from {url}...")
    text = extract_text_from_pdf(url)
    if text:
        print(f"Extracted {len(text)} characters.")
        print("First 500 characters:")
        print(text[:500])
    else:
        print("Failed to extract text.")
