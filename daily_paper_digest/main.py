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
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not set in .env")
        return

    # 1. Fetch papers
    print("Fetching daily papers...")
    papers = fetch_daily_papers()
    print(f"Found {len(papers)} papers.")
    
    relevant_count = 0
    
    for paper in papers:
        title = paper['title']
        summary = paper['summary']
        pdf_link = paper['pdf_link']
        
        # 2. Check relevance
        print(f"Checking relevance for: {title}")
        is_relevant, reason = check_relevance(title, summary, keywords)
        time.sleep(2) # Rate limit politeness
        
        if is_relevant:
            print(f"-> RELEVANT ({reason}). Analyzing...")
            relevant_count += 1
            
            # 3. Extract text
            text = extract_text_from_pdf(pdf_link)
            if not text:
                print("-> Failed to extract text. Skipping.")
                continue
                
            # 4. Analyze
            report = analyze_paper(text)
            
            # 5. Send to Discord
            
            # Header
            header = f"📄 **{title}**\n🔗 {paper['link']}\n\n**Relevance:** {reason}\n"
            send_discord_message(webhook_url, header)
            
            # Report (Structured)
            send_markdown_report(webhook_url, report)
            
            # Separator
            send_discord_message(webhook_url, "✨ --------------------------------------------------------------------- ✨")
            
        else:
            print("-> Not relevant.")
            
    print(f"[{datetime.now()}] Job complete. Sent {relevant_count} reports.")

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
