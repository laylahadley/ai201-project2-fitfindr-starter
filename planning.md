# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->


**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): ...
- `new_item` (dict): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"


**What FitFindr Does:**
FitFindr is an AI agent that parses a user's natural language request for secondhand clothing, triggering a search tool to find matches in a mock database, and sequentially passes those results to an outfit suggester and a social-media caption generator. If a step fails, such as the search tool returning zero matches, the agent immediately halts the tool chain, informs the user of the failure, and requests modified search criteria rather than passing empty data to the next tool.

**Trace Example:**
* **User Query:** "I'm looking for a vintage graphic tee under $30, size M. I mostly wear baggy jeans and chunky sneakers."
     * **Step 1:** The agent calls `search_listings(description="vintage graphic tee", size="M", max_price=30.0)`. It finds a match (e.g., a $22 Faded Band Tee) and holds it in the session state.
     * **Step 2:** The agent calls `suggest_outfit(new_item=<band tee>, wardrobe=<user's wardrobe>)`. It returns styling advice based on the user's baggy jeans and chunky sneakers. 
     * **Step 3:** The agent calls `create_fit_card(outfit=<suggestion>, new_item=<band tee>)` to generate a short, shareable text snippet summarizing the thrifted find and the outfit.
     **Final output to user:** 
     Based on the example trace, the final output would look something like this:"I found a great match for you! I tracked down a Faded Band Tee in size M for $22 on Depop.
     How to style it:
     Pair this with your wide-leg jeans and platform Docs for a classic 90s grunge look. Roll the sleeves once and tuck the front corner slightly for shape.
     Your Fit Card:
     thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories"



---------------------------------------------------------------------
ORIGINAL PLANNING.MD OUTPUT - GEMINI
# FitFindr Planning Document

## 1. Tool Inventory & AI Tool Plan
* **`search_listings(description: str, size: str, max_price: float) -> list[dict]`**
  * **Input:** Description of the item (e.g., "vintage denim jacket"), size preference, and a maximum price.
  * **Output:** A list of dictionary objects representing mock clothing listings matching the criteria.
  * **Purpose:** Acts as the primary search mechanism to query the mock dataset for secondhand clothing.

* **`suggest_outfit(new_item: dict, wardrobe: list[dict]) -> list[str]`**
  * **Input:** A dictionary representing the newly found item, and a list of dictionaries representing the user's current wardrobe items.
  * **Output:** A list of strings, each describing a potential outfit combination.
  * **Purpose:** Helps the user visualize how the new item integrates with what they already own.

* **`create_fit_card(outfit: str, new_item: dict) -> str`**
  * **Input:** A string describing the chosen outfit and the dictionary of the newly found item.
  * **Output:** A short, punchy string designed for social media sharing (e.g., an Instagram caption).
  * **Purpose:** Summarizes the final style choice in a fun, shareable format.

## 2. Planning Loop and State Management
The agent will operate using a ReAct (Reasoning and Acting) or sequential planning loop via the Groq LLM. 
* **State Management:** A central `session_state` dictionary (or context history) will be maintained during the execution loop. When `search_listings` returns an item, it will be appended to the current state context so that when the agent decides to call `suggest_outfit`, it has direct access to the exact item dictionary without asking the user to re-input details.
* **Planning Loop:** The LLM receives the user prompt and available tools. It will first call `search_listings`. Upon receiving the result back in the prompt context, it will reason that it needs to integrate the item into the wardrobe, calling `suggest_outfit`. Finally, upon receiving the outfit ideas, it will call `create_fit_card`.

## 3. Error-Handling Table & Interaction Walkthrough

| Tool | Potential Error / Failure Mode | Agent Fallback Strategy |
| :--- | :--- | :--- |
| `search_listings` | Returns an empty list (no matches found). | The agent will inform the user that no items matched the specific criteria and ask if they would like to increase the `max_price` or broaden the `description`. |
| `suggest_outfit` | User's `wardrobe` array is empty or missing. | The agent will generate a "capsule" outfit suggestion using standard basics (e.g., plain white tee, classic blue jeans) to show how the item could be styled generally. |
| `create_fit_card` | Model fails to format output or returns empty string. | The agent will utilize a hardcoded fallback template string: *"Snagged this [Item Name]! Ready to pair it with my [Outfit Element]. #ThriftScore"* |

## 4. Architecture Diagram
```mermaid
graph TD
    User([User Request]) --> Agent[AI Agent Controller]
    Agent -->|State/Context| SessionState[(Session State)]
    
    Agent -->|1. Call search_listings| Tool1[search_listings]
    Tool1 -->|Return matches or empty| Agent
    
    Agent -->|2. Call suggest_outfit| Tool2[suggest_outfit]
    Tool2 -->|Return outfit ideas| Agent
    
    Agent -->|3. Call create_fit_card| Tool3[create_fit_card]
    Tool3 -->|Return social caption| Agent
    
    Agent --> FinalResponse([Final Fit Card to User])