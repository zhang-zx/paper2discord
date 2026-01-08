# Daily Paper Digest Agent

This agent checks Hugging Face Papers daily, filters them based on your interests using Gemini, and sends a deep research summary to your Discord.

## Setup

1.  **Install Dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r daily_paper_digest/requirements.txt
    ```

2.  **Configuration:**
    -   Edit `daily_paper_digest/config.yaml` to set your interested **keywords** and the **schedule time**.
    -   Edit `daily_paper_digest/.env` and add your API keys:
        ```env
        GEMINI_API_KEY=your_gemini_api_key
        DISCORD_WEBHOOK_URL=your_discord_webhook_url
        ```

## Usage

### Run Manually (Once)
To trigger the check immediately (useful for testing):
```bash
./daily_paper_digest/venv/bin/python run.py --run-now
```

### Run as a Daemon (Scheduler)
To start the daily scheduler (runs at 10 PM ET by default):
```bash
./daily_paper_digest/venv/bin/python run.py
```
Keep this process running (e.g., using `tmux`, `screen`, or a systemd service).

## Project Structure
-   `daily_paper_digest/scraper.py`: Fetches papers from Hugging Face.
-   `daily_paper_digest/content_extractor.py`: Downloads and reads PDFs.
-   `daily_paper_digest/analyzer.py`: Uses Gemini to check relevance and summarize.
-   `daily_paper_digest/discord_notifier.py`: Sends reports to Discord.
-   `daily_paper_digest/main.py`: Main logic and scheduler.
