from huggingface_hub import list_daily_papers
import datetime

def fetch_daily_papers(date=None):
    """
    Fetches the list of papers from Hugging Face Papers for the given date.
    If date is None, fetches for the current date (UTC).
    Returns a list of dictionaries containing title, id, and link.
    """
    if date is None:
        # Defaults to today UTC to align with Hugging Face server time
        # This prevents "date must be less than or equal to..." errors if local time is ahead
        target_date = datetime.datetime.now(datetime.timezone.utc).date()
    else:
        target_date = date

    try:
        # list_daily_papers returns an iterator. We must consume it to trigger the API call and catch errors.
        papers_data = list(list_daily_papers(date=target_date))
    except Exception as e:
        # If today fails (e.g., timezone mismatch causing "future date" error), try yesterday
        if "must be less than" in str(e) or "Bad request" in str(e) or "400" in str(e):
            print(f"Warning: Fetching for {target_date} failed ({e}). Trying yesterday.")
            target_date = target_date - datetime.timedelta(days=1)
            try:
                papers_data = list(list_daily_papers(date=target_date))
            except Exception as e2:
                print(f"Error fetching papers for {target_date}: {e2}")
                return []
        else:
            print(f"Error fetching papers: {e}")
            return []

    papers = []
    
    for paper in papers_data:
        # The paper object has attributes like title, paper_id, etc.
        # We need to inspect the object structure or assume standard attributes.
        # Based on docs, it should have 'title' and 'paper_id'.
        
        # Construct links
        # paper_id is usually the arxiv id
        if hasattr(paper, 'paper_id'):
            paper_id = paper.paper_id
        elif hasattr(paper, 'id'):
             paper_id = paper.id
        else:
             # Fallback or error
             print(f"Unknown paper structure: {paper}")
             continue

        title = paper.title
        summary = getattr(paper, 'summary', '')
        
        papers.append({
            "title": title,
            "summary": summary,
            "id": paper_id,
            "link": f"https://huggingface.co/papers/{paper_id}",
            "pdf_link": f"https://arxiv.org/pdf/{paper_id}.pdf",
            "arxiv_link": f"https://arxiv.org/abs/{paper_id}"
        })
        
    return papers

if __name__ == "__main__":
    # Test the scraper
    todays_papers = fetch_daily_papers()
    print(f"Found {len(todays_papers)} papers today.")
    for p in todays_papers[:3]:
        print(f"- {p['title']} ({p['id']})")