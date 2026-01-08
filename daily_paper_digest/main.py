import schedule
import time
import yaml
import os
import argparse
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz

from daily_paper_digest.scraper import fetch_daily_papers
from daily_paper_digest.content_extractor import extract_text_from_pdf
from daily_paper_digest.analyzer import check_relevance, analyze_paper
from daily_paper_digest.discord_notifier import send_discord_message, send_markdown_report

# Load environment variables
load_dotenv()

def load_config():
    with open("daily_paper_digest/config.yaml", "r") as f:
        return yaml.safe_load(f)

def run_daily_digest():
    print(f"[{datetime.now()}] Starting Daily Paper Digest...")
    
    config = load_config()
    keywords = config.get("keywords", [])
    categories = config.get("categories", [])
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not set in .env")
        return

    # 1. Fetch papers
    print("Fetching daily papers...")
    papers = fetch_daily_papers()
    print(f"Found {len(papers)} papers.")
    
    relevant_papers = []
    
    # 2. Filter and Score Relevance
    for paper in papers:
        title = paper['title']
        summary = paper['summary']
        
        print(f"Checking relevance for: {title}")
        is_relevant, score, category, reason = check_relevance(title, summary, keywords, categories)
        time.sleep(1) # Rate limit politeness
        
        if is_relevant:
            print(f"-> RELEVANT (Score: {score}, Category: {category}).")
            paper['relevance_score'] = score
            paper['relevance_reason'] = reason
            paper['category'] = category
            relevant_papers.append(paper)
        else:
            print("-> Not relevant.")
            
    # 3. Select Top N based on config
    max_papers = config.get("max_papers", 5)
    relevant_papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    top_papers = relevant_papers[:max_papers]
    
    print(f"Selected {len(top_papers)} top papers from {len(relevant_papers)} relevant ones.")

    # 4. Group by category
    grouped_papers = {}
    for paper in top_papers:
        cat = paper.get('category', 'General AI')
        if cat not in grouped_papers:
            grouped_papers[cat] = []
        grouped_papers[cat].append(paper)

    # 5. Analyze and Send by Category
    for cat_name, papers_in_cat in grouped_papers.items():
        # Find category info for emoji
        cat_info = next((c for c in categories if c['name'] == cat_name), {'emoji': '🤖'})
        
        # Create a THREAD (Forum Post) for this category
        date_str = datetime.now().strftime("%Y-%m-%d")
        thread_title = f"{cat_info['emoji']} {cat_name} - {date_str}"
        
        # Send Header Message which creates the forum post (thread)
        print(f"Creating thread: {thread_title}")
        header_text = f"Found {len(papers_in_cat)} papers for **{cat_name}**."
        
        # Pass thread_name to create a new thread/post
        thread_id = send_discord_message(webhook_url, header_text, thread_name=thread_title)
        
        if not thread_id:
            print("Failed to create thread, falling back to main channel context.")
        
        for paper in papers_in_cat:
            title = paper['title']
            pdf_link = paper['pdf_link']
            reason = paper['relevance_reason']
            score = paper['relevance_score']
            
            print(f"Analyzing Top Paper: {title} (Score: {score})")
            
            # 4a. Extract text
            text = extract_text_from_pdf(pdf_link)
            if not text:
                print("-> Failed to extract text. Skipping.")
                continue
                
            # 4b. Deep Research Analysis
            report = analyze_paper(text)
            
            # 5. Send to Discord
            
            # Header
            header = f"📄 **{title}**\n🔗 <{paper['link']}>\n\n**Relevance (Score: {score}/10):** {reason}\n"
            send_discord_message(webhook_url, header, thread_id=thread_id)
            
            # Report (Structured)
            send_markdown_report(webhook_url, report, thread_id=thread_id)
            
            # Separator
            send_discord_message(webhook_url, "✨ --------------------------------------------------------------------- ✨", thread_id=thread_id)
            
    print(f"[{datetime.now()}] Job complete. Sent {len(top_papers)} reports.")

def start_scheduler():
    config = load_config()
    schedule_time_str = config.get("schedule_time", "22:00")
    
    print(f"Scheduler started. Running daily at {schedule_time_str} ET.")
    
    et_tz = pytz.timezone('US/Eastern')
    
    while True:
        now_et = datetime.now(et_tz)
        current_time = now_et.strftime("%H:%M")
        
        # Check if matches schedule time
        # We also need to ensure we don't run multiple times in the same minute
        # But since we sleep 60s, it's roughly okay, but safer to check if we already ran today.
        
        # Actually, simpler logic:
        # Calculate next run time.
        
        today_target = now_et.replace(
            hour=int(schedule_time_str.split(":")[0]),
            minute=int(schedule_time_str.split(":")[1]),
            second=0,
            microsecond=0
        )
        
        if now_et >= today_target:
            # Schedule for tomorrow
            next_run = today_target + timedelta(days=1)
        else:
            next_run = today_target
            
        # Ensure next_run is a weekday (Mon=0, Fri=4)
        # If Saturday (5), add 2 days -> Monday
        # If Sunday (6), add 1 day -> Monday
        while next_run.weekday() >= 5:
             print(f"Skipping weekend run on {next_run.strftime('%A')}")
             next_run += timedelta(days=1)
            
        wait_seconds = (next_run - now_et).total_seconds()
        
        print(f"Next run in {wait_seconds/3600:.2f} hours (at {next_run} ET).")
        time.sleep(wait_seconds)
        
        run_daily_digest()
        # Sleep a bit to avoid double triggering if calculation was slightly off
        time.sleep(60) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run the digest immediately")
    args = parser.parse_args()
    
    if args.run_now:
        run_daily_digest()
    else:
        start_scheduler()
