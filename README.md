# 📑 Daily Paper Digest

> **Your personal AI Research Assistant, powered by Google Gemini.**

This agent automates your research workflow by checking **Hugging Face Papers** daily, filtering them based on your specific interests, and delivering deep, structured analytical reports to your **Discord Server**.

## ✨ Key Features

*   **🧠 Intelligent Filtering**: Uses `gemini-2.0-flash-lite` to score papers (1-10) based on your keywords. No more noise.
*   **📂 Smart Categorization**: Automatically groups papers into custom categories (e.g., "🎥 Generative Media", "⚡ Model Efficiency") using AI classification.
*   **🔬 Deep Analysis**: Uses the powerful `gemini-3-pro-preview` to generate comprehensive summaries, extracting key findings, methodologies, and code links.
*   **💬 Organized Threads**: Designed for **Discord Forum Channels**. Creates a dedicated thread for each category daily, keeping your feed clean.
*   **⏰ Precision Scheduling**: Runs automatically at **23:00 UTC** (Mon-Fri) via GitHub Actions, aligned perfectly with Hugging Face's daily reset.

---

## 🚀 Setup for GitHub Actions (Automated Daily Run)

1.  **Create/Fork Repository:**
    Create a new **private** repository and push this code to it.

2.  **Configure Secrets:**
    Go to your repository **Settings** > **Secrets and variables** > **Actions**.
    Click **New repository secret** and add the following:

    | Secret Name | Value Description |
    | :--- | :--- |
    | `GEMINI_API_KEY` | Your Google Gemini API Key. |
    | `DISCORD_WEBHOOK_URL` | **Important:** Must be a Webhook for a **Discord Forum Channel** (not a text channel). |
    | `APP_CONFIG` | Copy the **entire content** of `daily_paper_digest/config.example.yaml` (or your custom version), edit it with your keywords, and paste the text here. |

    > **Why `APP_CONFIG`?** This keeps your research interests private and allows the agent to build the configuration file dynamically during the automated run.

3.  **Verification:**
    Go to the **Actions** tab, select "Daily Paper Digest", and click **Run workflow** to test it immediately.

---

## 💻 Local Development

### 1. Installation
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/daily-paper-digest.git
cd daily-paper-digest

# Setup Virtual Env
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r daily_paper_digest/requirements.txt
```

### 2. Configuration
The actual config file is git-ignored for security. Create it from the example:

```bash
cp daily_paper_digest/config.example.yaml daily_paper_digest/config.yaml
```
Edit `daily_paper_digest/config.yaml` to set your **keywords** and **categories**.

### 3. Environment Variables
Create a `.env` file in `daily_paper_digest/.env`:
```
GEMINI_API_KEY=your_key_here
DISCORD_WEBHOOK_URL=your_forum_webhook_url
```

### 4. Run Manually
```bash
# Run immediately (Debug mode)
./daily_paper_digest/venv/bin/python run.py --run-now

# Run scheduler (Daemon mode - runs at 23:00 UTC)
./daily_paper_digest/venv/bin/python run.py
```

---

## ⚙️ Configuration Options (`config.yaml`)

```yaml
# Research Keywords
keywords:
  - "video generation"
  - "agentic workflows"

# Reporting Categories
categories:
  - name: "Generative Media"
    emoji: "🎥"
    description: "Video, image, audio generation."
  - name: "Agents"
    emoji: "🤖"
    description: "Autonomous agents and planning."

# Max papers to analyze per run
max_papers: 5
```
