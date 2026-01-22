# Daily Paper Digest

## Project Overview
**Daily Paper Digest** is an automated AI agent designed to keep researchers up-to-date with the latest advancements in AI. It scrapes daily papers from Hugging Face, intelligently filters them based on user-defined research interests, groups them by category, and performs deep analysis using Google's Gemini models. The final reports are delivered to a Discord server (specifically optimized for Forum Channels).

### Key Features
*   **Intelligent Filtering:** Uses `gemini-2.0-flash-lite` to score relevance (1-10) and classify papers into categories (e.g., "Generative Media", "Model Efficiency").
*   **Deep Analysis:** Uses `gemini-3-pro-preview` to generate comprehensive research summaries, extracting key findings, methodologies, and community resources (GitHub code, Reddit threads, etc.).
*   **Forum Organization:** Automatically creates a new thread for each category in a Discord Forum Channel (e.g., "🎥 Generative Media - 2026-01-08") to keep discussions organized.
*   **Robust Automation:** Runs on a strict UTC schedule via GitHub Actions to align with Hugging Face's server time, with built-in retry logic for API rate limits.

## Architecture & Technologies
*   **Language:** Python 3.10+
*   **AI Models:**
    *   **Relevance/Categorization:** `gemini-2.0-flash-lite-preview-02-05` (Fast & Cheap)
    *   **Deep Analysis:** `gemini-3-pro-preview` (High Reasoning)
*   **Data Source:** Hugging Face Papers (`huggingface_hub`) + arXiv PDF extraction (`pypdf`).
*   **Integration:** Discord Webhooks (Forum Channel support).
*   **Scheduling:** GitHub Actions (Primary) or Local `schedule` library (Development).

## Building and Running

### Prerequisites
*   Python 3.10+
*   A Google Gemini API Key
*   A Discord Webhook URL (pointed to a **Forum Channel**)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd daily-paper-digest
    ```
2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r daily_paper_digest/requirements.txt
    ```
4.  **Configuration:**
    *   Create a `.env` file in `daily_paper_digest/.env` (or set environment variables):
        ```
        GEMINI_API_KEY=your_key_here
        DISCORD_WEBHOOK_URL=your_webhook_url
        ```
    *   Edit `daily_paper_digest/config.yaml` to customize keywords and categories.

### Running the Agent
**Manual / Immediate Run (Debug Mode):**
```bash
# From project root
./daily_paper_digest/venv/bin/python run.py --run-now
```

**Daemon Mode (Local Scheduler):**
```bash
# Starts the scheduler process (blocks terminal)
./daily_paper_digest/venv/bin/python run.py
```

## Development Conventions

### Timezone & Scheduling
*   **Strict UTC:** All time operations, scheduling, and date string generation must use **UTC** (`pytz.utc` or `datetime.timezone.utc`).
*   **Schedule:** The agent runs at **23:00 UTC** (Monday-Friday), which is 1 hour before the Hugging Face daily paper reset.

### Discord Formatting
*   **No Embeds:** All external links (arXiv, GitHub, Twitter) must be wrapped in `< >` (e.g., `<https://arxiv.org...>`) to prevent Discord from generating large, cluttering preview cards.
*   **Forum Threads:** The agent expects the Webhook to be for a **Forum Channel**. It creates a thread per category using the `thread_name` payload field.

### Code Structure
*   `daily_paper_digest/scraper.py`: Handles paper fetching (includes "yesterday" fallback logic for empty days).
*   `daily_paper_digest/analyzer.py`: Contains all Gemini API interaction logic.
*   `daily_paper_digest/discord_notifier.py`: Handles message splitting and webhook retries (handles 429 rate limits).
*   `daily_paper_digest/main.py`: Main orchestration loop and local scheduler.
