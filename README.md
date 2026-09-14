# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

FitFindr is a multi-tool AI agent that helps users find secondhand clothing pieces and figure out how to wear them. It orchestrates a set of tools in response to natural language requests, evaluating fit against an existing wardrobe, generating shareable outfit descriptions, and handling tool failures gracefully.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query:**
vintage graphic tee under 30 

**Step 1 — Tool called:** 
- Tool: `search_listings`
- Input: `description` (str), `size` (str or None), `max_price` (float or None)
- Why this tool: Searches the mock dataset for secondhand clothing. 
- Output: A list of dictionaries representing matching listings. 

**Step 2 — Tool called:**
- Tool: `suggest_outfit` 
- Input: `new_item` (dict), `wardrobe` (dict).
- Why this tool: Helps the user visualize how the new item integrates with their wardrobe. 
- Output: A string containing 1-2 sentences of styling advice.

**Step 3 — Tool called:**
- Tool: `create_fit_card`
- Input: `outfit` (str), `new_item` (dict).
- Why this tool: Summarizes the final style choice in a shareable format. 
- Output: A short string designed for social media sharing.

**Final output to user:**
🛍️ Top listing found:
Found: Y2K Baby Tee — Butterfly Print - $18.0
Platform: depop

👗 Outfit Idea:
Pair this Y2K butterfly baby tee with high-waisted, neutral-wash denim jeans to balance the playful print. Finish the look with simple white sneakers for a clean, effortless vibe.

✨Your fit card:
$18 thrift find 💸 This Y2K butterfly tee + high-waisted denim is the perfect balance of playful and clean. Effortless Y2K energy in white sneakers. ✨

---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` |If no listings match, the tool returns an empty list. The agent catches this, halts the loop, and outputs: *"No items matched your exact criteria. Try increasing your budget or broadening the description!"* (Verified in terminal testing). | |
| `suggest_outfit` |If the user's wardrobe is completely empty, the tool intercepts the empty array and alters its LLM prompt to suggest a "capsule" outfit using standard basics (like plain tees or standard denim) instead of crashing. | |
| `create_fit_card` |If the previous tool fails and passes an empty string, this tool catches it with an `if not outfit:` guard clause and safely returns: *"Cannot generate fit card: no outfit suggestion provided."* | |

---

## Spec Reflection

The final implementation closely matches my initial `planning.md` spec. The state management behaves exactly as diagrammed, specifically the early-exit branch when `search_listings` returns an empty array. The main deviation was updating the model from `meta-llama` to `qwen` after discovering the initial model returned empty strings for the outfit suggestion tool.
<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
Writing out the precise inputs, outputs, and failure modes in planning.md made using AI coding assistants like Claude Code and Cursor significantly more effective. Because the architecture diagram and conditional logic were already defined, I could feed the exact specifications to the AI to generate the run_agent() loop. This prevented the LLM from making incorrect assumptions about how state should be passed or what to do when search_listings returned an empty array, saving a massive amount of debugging time.

**One divergence from your spec, and why:**
One major divergence from the original specification was changing the assigned Groq LLM from the Llama family to a Qwen model during implementation. The originally specified models were either unavailable on the current API tier or silently failing by returning completely empty strings for the outfit suggestion tool. Additionally, I had to modify the agent loop code to include a strict max_tokens=150 parameter because the new model attempted to reserve too many output tokens for simple JSON extraction, which immediately triggered rate limit errors.
---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

## Demo video
see demo video here --> [https://youtu.be/Ya-3KfYsiGQ]


