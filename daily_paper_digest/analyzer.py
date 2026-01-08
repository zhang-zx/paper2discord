from google import genai
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def check_relevance(title, summary, keywords, categories=None):
    """
    Asks Gemini if the paper is relevant based on title, summary and keywords.
    Also classifies the paper into a category if categories are provided.
    Returns (bool, score, category, reason). Score is 1-10.
    """
    if not client:
        print("GEMINI_API_KEY not found.")
        return False, 0, "Other", "Missing API Key"

    model_id = 'gemini-2.0-flash-lite-preview-02-05'
    
    categories_str = ""
    if categories:
        categories_str = "Categories: " + ", ".join([c['name'] for c in categories])

    prompt = f"""
    I have a list of keywords indicating my research interests: {keywords}.
    {categories_str}
    
    Here is a paper:
    Title: {title}
    Abstract: {summary}
    
    Tasks:
    1. Is this paper relevant to my interests? Answer "YES" or "NO".
    2. Provide a relevance score from 1 to 10 (10 being highly relevant).
    3. If relevant, select the best category from the list above. If none fit well, use "General AI".
    4. Provide a very brief explanation.
    
    Format your response as:
    DECISION: [YES/NO]
    SCORE: [SCORE]
    CATEGORY: [CATEGORY NAME]
    REASON: [REASON]
    """
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        text = response.text.strip()
        
        decision = "NO"
        score = 0
        category = "General AI"
        reason = ""
        
        for line in text.split('\n'):
            if line.startswith("DECISION:"):
                decision = line.replace("DECISION:", "").strip().upper()
            elif line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE:", "").strip())
                except:
                    score = 0
            elif line.startswith("CATEGORY:"):
                category = line.replace("CATEGORY:", "").strip()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
        
        if decision == "YES":
            return True, score, category, reason
        else:
            return False, score, category, reason
            
    except Exception as e:
        print(f"Error checking relevance: {e}")
        return False, 0, "General AI", str(e)

def analyze_paper(text):
    """
    Performs deep research analysis on the full paper text.
    Returns a markdown formatted report.
    """
    if not client:
        return "Error: Missing API Key"

    model_id = 'gemini-3-pro-preview'
    
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
    (Identify 3-5 highly relevant papers. Format as a list: `- [Title](<Link>)`. If no direct link in text, use `https://scholar.google.com/scholar?q=TITLE`)

    ## 6. 🔗 Resources & Community
    - **Code/Project:** Extract any GitHub repositories or Project Page URLs mentioned in the text. Wrap the URL in < > like `<url>`. If none are found, state "Not found in text".
    - **Community Sentiment:** Provide search links for this paper title on:
      - [Twitter/X](<https://twitter.com/search?q=TITLE>)
      - [Reddit](<https://www.reddit.com/search/?q=TITLE>)
      - [Hacker News](<https://hn.algolia.com/?q=TITLE>)
      (Replace TITLE with the URL-encoded paper title)
    
    Paper Content (Truncated):
    {text[:100000]} 
    """
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error analyzing paper: {e}"

if __name__ == "__main__":

    # Test relevance

    keywords = ["LLM", "agent"]

    categories = [{"name": "Generative Media"}, {"name": "Model Efficiency"}]

    title = "Large Language Models as Agents"

    summary = "We show that LLMs can act as agents."

    print("Checking relevance...")

    rel, score, category, reason = check_relevance(title, summary, keywords, categories)

    print(f"Relevant: {rel}, Score: {score}, Category: {category}, Reason: {reason}")


