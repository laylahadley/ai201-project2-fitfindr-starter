"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""


import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from utils.data_loader import load_listings

# load environment variables from .env
load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: Optional[str] = None,
    max_price: Optional[float] = None
) -> list[dict]:
    """
    Search mock listings dataset matching description, size, and max_price.
    Returns a list of matching item dictionaries or an empty list if no matches.
    """
    try:
        listings = load_listings()
    except Exception as e:
        print(f"Error loading listings: {e}")
        return []

    query = description.lower() if description else ""
    results = []

    for item in listings:
        # 1. Check description match across title, description, and style_tags
        title = item.get("title", "").lower()
        desc = item.get("description", "").lower()
        tags = " ".join(item.get("style_tags", [])).lower()
        searchable_text = f"{title} {desc} {tags}"

        # Match any search term if multiple words are provided
        keywords = query.split()
        if keywords and not any(kw in searchable_text for kw in keywords):
            continue

        # 2. Check size filter (if specified and not None)
        if size and item.get("size") != size:
            continue

        # 3. Check price filter (if specified and not None)
        if max_price is not None and item.get("price", 0) > max_price:
            continue

        results.append(item)

    return results


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: Optional[dict] = None) -> str:
    """
    Suggests styling combinations using the new item and wardrobe.
    Handles empty or minimal wardrobe gracefully.
    """
    if not new_item or not isinstance(new_item, dict):
        return "No item was provided to style."

    # Extract wardrobe items safely
    items = []
    if wardrobe and isinstance(wardrobe, dict):
        items = wardrobe.get("items", [])

    item_summary = (
        f"{new_item.get('title', 'Item')} "
        f"({new_item.get('brand', 'Unknown brand')}, {new_item.get('size', 'N/A')}, "
        f"Condition: {new_item.get('condition', 'N/A')})"
    )

    # Empty wardrobe fallback prompt
    if not items:
        system_prompt = (
            "You are a concise personal stylist. The user's wardrobe is empty. "
            "Suggest 1-2 sentences of styling advice for the item using standard, "
            "everyday wardrobe staples (such as basic white tees, neutral denim, or simple sneakers)."
        )
        user_prompt = f"How should I style this piece: {item_summary}?"
    else:
        wardrobe_desc = "\n".join(
            f"- {i.get('name', 'Item')} ({i.get('category', '')}, {i.get('color', '')}, style: {i.get('style', '')})"
            for i in items
        )
        system_prompt = (
            "You are a concise personal stylist. Suggest an outfit combining the new thrifted item "
            "with pieces from the user's wardrobe. Keep your suggestion to 1-2 direct, actionable sentences."
        )
        user_prompt = (
            f"New thrifted item:\n{item_summary}\n\n"
            f"My current wardrobe:\n{wardrobe_desc}\n\n"
            "Suggest a cohesive outfit combination."
        )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Styling suggestion unavailable: {e}"


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generates a punchy, shareable Instagram-style caption for the completed outfit.
    Guards against empty outfit strings.
    """
    if not outfit or not outfit.strip():
        return "Cannot generate fit card: no outfit suggestion provided."

    if not new_item or not isinstance(new_item, dict):
        return "Cannot generate fit card: missing item details."

    item_title = new_item.get("title", "thrifted find")
    price = new_item.get("price", "")
    platform = new_item.get("platform", "online")

    system_prompt = (
        "You write punchy, authentic social media captions (like Instagram or Depop) "
        "for thrifted outfits. Include 1-2 relevant emojis, mention the thrift find, "
        "and keep it under 30 words."
    )
    user_prompt = (
        f"Item: {item_title} (Thrifted for ${price} on {platform})\n"
        f"Outfit: {outfit}\n"
        "Write a shareable fit card caption."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.85,  # Higher temperature ensures diverse outputs
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"thrifted this {item_title} for ${price}! Ready to style it up. #ThriftScore"