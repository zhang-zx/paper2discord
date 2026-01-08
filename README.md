# Daily Paper Digest Agent

This agent checks Hugging Face Papers daily, filters them based on your interests using Gemini, and sends a deep research summary to your Discord.

## Setup for GitHub Actions (Automated Daily Run)

1.  **Create a Repository:**
    -   Go to GitHub and create a new **private** repository (e.g., `daily-paper-digest`).

2.  **Push Code:**
    Run these commands in your terminal:
    ```bash
    # (Optional) Rename branch to main
    git branch -m main
    
    # Add your remote repository URL
    git remote add origin https://github.com/YOUR_USERNAME/daily-paper-digest.git
    
    # Push code
    git push -u origin main
    ```

3.  **Configure Secrets:**
    -   Go to your repository **Settings** > **Secrets and variables** > **Actions**.
    -   Click **New repository secret** and add:
        -   Name: `GEMINI_API_KEY`, Value: (Your Gemini API Key)
        -   Name: `DISCORD_WEBHOOK_URL`, Value: (Your Discord Webhook URL)

4.  **Verification:**
    -   Go to the **Actions** tab in your repository.
    -   Select "Daily Paper Digest" from the left sidebar.
    -   You can wait for the scheduled time or click **Run workflow** manually to test it.

## Local Usage

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r daily_paper_digest/requirements.txt
```

### Run Manually
```bash
./daily_paper_digest/venv/bin/python run.py --run-now
```

## Configuration
Edit `daily_paper_digest/config.yaml` to change keywords. Commit and push changes to update the agent.