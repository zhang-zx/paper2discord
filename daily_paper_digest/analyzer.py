import google.generativeai as genai
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Handle missing key if necessary, or let it fail later
    pass
else:
    genai.configure(api_key=api_key)

def check_relevance(title, summary, keywords):
    """
    Asks Gemini if the paper is relevant based on title, summary and keywords.
    Returns (bool, reason).
    """
    if not api_key:
        print("GEMINI_API_KEY not found.")
        return False, "Missing API Key"

    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    prompt = f"""
    I have a list of keywords indicating my research interests: {keywords}.
    
    Here is a paper:
    Title: {title}
    Abstract: {summary}
    
    Is this paper relevant to my interests? 
    Answer with "YES" or "NO" followed by a very brief explanation.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.upper().startswith("YES"):
            return True, text
        else:
            return False, text
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return False, str(e)

def analyze_paper(text):
    """
    Performs deep research analysis on the full paper text.
    Returns a markdown formatted report.
    """
    if not api_key:
        return "Error: Missing API Key"

    model = genai.GenerativeModel('gemini-3-pro-preview')
    
    prompt = f"""
    You are an expert researcher using deep thinking. Read the paper and provide a high-quality summary report formatted for Discord.
    
    Structure the output strictly using these Markdown headers:
    
    ## 1. 💡 One-sentence Summary
    (A concise hook)
    
    ## 2. 🔑 Key Findings
    (3-5 concise bullet points. Focus on concepts and capability shifts. Omit specific benchmark numbers or leaderboard rankings unless they represent a massive breakthrough.)
    
    ## 3. 🧠 Key Takeaways
    (Why does this matter? What is the impact?)
    
    ## 4. 🛠️ Methodology
    (Briefly, how did they do it?)
    
    ## 5. 📚 Relation to Previous Work
    (Identify 3-5 highly relevant papers. Format as a list: `* [Title](Link)`. If no direct link in text, use `https://scholar.google.com/scholar?q=TITLE`)
    
    Paper Content (Truncated):
    {text[:100000]} 
    """
    # Note: 100k chars is well within Gemini 1.5 Pro/Flash limits (1M/2M tokens). 
    # But just in case, we truncate to avoid hitting very hard limits if text is garbage.
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing paper: {e}"

if __name__ == "__main__":
    # Test relevance
    keywords = ["LLM", "agent"]
    title = "Large Language Models as Agents"
    summary = "We show that LLMs can act as agents."
    print("Checking relevance...")
    rel, reason = check_relevance(title, summary, keywords)
    print(f"Relevant: {rel}, Reason: {reason}")
