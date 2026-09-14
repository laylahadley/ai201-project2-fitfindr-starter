"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""
import os
import json
from dotenv import load_dotenv 
from groq import Groq
from tools import search_listings, suggest_outfit, create_fit_card

# Load the environment variables before initializing the client
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "qwen/qwen3.8-27b"  # Updated model string

# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.
    """
    # Step 1: Initialize the session with _new_session().
    session = _new_session(query, wardrobe)

    # Step 2: Parse the user's query to extract parameters using the LLM.
    system_prompt = (
        "Extract search parameters from the user's clothing query. "
        "Respond ONLY with a valid JSON object containing exactly three keys: "
        "'description' (string, main item keywords), 'size' (string or null, exact size like 'M', 'L', 'XXS'), "
        "'max_price' (float or null, maximum price). Do not include markdown blocks."
    )
    
    try:
        response = client.chat.completions.create( 
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.1,
            max_tokens=150 
        ) 
        
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3].strip()
            
        session["parsed"] = json.loads(raw_content)
    except Exception as e:
        print(f"\n[DEBUG] LLM Error: {e}\n") # Add this print statement
        session["error"] = "I had trouble understanding those search parameters. Could you rephrase?"
        return session


    # Step 3: Call search_listings() with the parsed parameters.
    session["search_results"] = search_listings(
        description=session["parsed"].get("description", ""),
        size=session["parsed"].get("size"),
        max_price=session["parsed"].get("max_price")
    )

    # Check for empty results and return early
    if not session["search_results"]:
        session["error"] = "No items matched your exact criteria. Try increasing your budget or broadening the description!"
        return session

    # Step 4: Select the item to use (the top result).
    session["selected_item"] = session["search_results"][0]

    # Step 5: Call suggest_outfit() with the selected item and wardrobe.
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"]
    )

    # Step 6: Call create_fit_card() with the outfit suggestion and selected item.
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"]
    )

    # Step 7: Return the session.
    return session

# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
