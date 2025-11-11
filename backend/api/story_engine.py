import os
import random
from typing import Optional, List, Tuple
from openai import OpenAI

# --- Categories (public labels for UI) ---
CATEGORIES = {
    "magic_adventure": "Magic Adventure",
    "epic_quest": "Epic Quest",
    "mystery": "Mystery",
    "funny": "Funny",
    "friends_and_family": "Friends and Family",
    "furry_friends": "Furry Friends",
    "space_adventure": "Space Adventure",
    "boo": "Boo!",
}
CATEGORIES_PUBLIC: List[str] = list(CATEGORIES.values())

# Optional “inspiration anchors” (toggle via USE_INSPIRATION_SITES)
INSPIRATION_SITES = [
    "https://www.storyberries.com",
    "https://www.sleepystories.net",
    "https://www.freechildrenstories.com",
    "https://www.bedtimestory.ai",
]
USE_INSPIRATION = os.getenv("USE_INSPIRATION_SITES", "1") == "1"

def _insp_storyteller() -> str:
    if USE_INSPIRATION and INSPIRATION_SITES:
        return ("Write a fresh, original story that is *inspired by* (never copies) kid-lit patterns you might see on: "
                + ", ".join(INSPIRATION_SITES) + ".")
    return ("Write a fresh, original story drawing on classic children's storytelling patterns—clear arcs, gentle stakes, "
            "warmth, and reassuring endings—without referencing external sources.")

def _insp_judge() -> str:
    if USE_INSPIRATION and INSPIRATION_SITES:
        return ("Originality: phrasing must remain unique; you may draw *subtle* inspiration from kid-safe public story "
                "collections like " + ", ".join(INSPIRATION_SITES) + " without copying.")
    return ("Originality: phrasing must remain unique; draw only on classic children's storytelling patterns (clear arcs, "
            "gentle stakes, warmth) without referencing external sources.")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Technique library (many-to-many with categories) ---
TECHNIQUES = {
    "Clear Arc (B-M-E)": "Use a clear three-part arc: cozy beginning, gentle middle challenge, happy resolution.",
    "Rule of Three": "Use three beats, helpers, or tries.",
    "Show, Don't Tell": "Show feelings via actions and dialogue, not explanations.",
    "Sensory Details": "Kid-friendly sensory details (sound, color, smell, textures).",
    "Kid Dialogue": "Short, lively lines; clear speaker tags.",
    "Positive Moral": "Gentle moral (cooperation, kindness, courage) woven naturally.",
    "Humor & Surprise": "Small, safe surprises or wordplay; warm humor.",
    "Figurative Light": "Light similes/metaphors kids get (e.g., 'soft as a marshmallow cloud').",
    "Safe Stakes": "Conflict remains gentle and safe for ages 5–10.",
    "Rhythm & Repetition": "Light repetition/rhythm without tedium.",
    "Vocabulary Ceiling": "Roughly Grade 2–4; explain rare words in context.",
    "World Seeds": "Snacks, pets, cozy rooms, friendly robots—anchors kids love.",
    "Category Flavor: Magic Adventure": "Magical helper/tool; whimsical rule; fair outcomes.",
    "Category Flavor: Epic Quest": "Simple map, three small trials, friendly guide, clear goal.",
    "Category Flavor: Mystery": "Fair visible clues; silly (not scary) red herrings; tidy reveal.",
    "Category Flavor: Funny": "Exaggeration, harmless mishaps; end with a giggle and a hug.",
    "Category Flavor: Friends and Family": "Home/school setting; teamwork, empathy, sharing, reassurance.",
    "Category Flavor: Furry Friends": "Animal sidekick with a quirk; show care/responsibility.",
    "Category Flavor: Space Adventure": "Cozy sci-fi: friendly alien, soft rockets, wonder about stars.",
    "Category Flavor: Boo!": "Spooky-but-safe: giggly ghosts, glow comfort, reassuring end.",
    "Clue Economy": "Keep clues visible and simple; reveal gently.",
}

CATEGORY_TECHNIQUE_MAP = {
    "Magic Adventure": ["Clear Arc (B-M-E)", "Rule of Three", "Show, Don't Tell", "Sensory Details", "Kid Dialogue", "Positive Moral", "Figurative Light", "Category Flavor: Magic Adventure"],
    "Epic Quest": ["Clear Arc (B-M-E)", "Rule of Three", "World Seeds", "Kid Dialogue", "Positive Moral", "Safe Stakes", "Category Flavor: Epic Quest"],
    "Mystery": ["Clear Arc (B-M-E)", "Clue Economy", "Show, Don't Tell", "Kid Dialogue", "Positive Moral", "Safe Stakes", "Category Flavor: Mystery"],
    "Funny": ["Clear Arc (B-M-E)", "Humor & Surprise", "Rhythm & Repetition", "Kid Dialogue", "World Seeds", "Positive Moral", "Category Flavor: Funny"],
    "Friends and Family": ["Clear Arc (B-M-E)", "Show, Don't Tell", "Kid Dialogue", "World Seeds", "Positive Moral", "Safe Stakes", "Category Flavor: Friends and Family"],
    "Furry Friends": ["Clear Arc (B-M-E)", "Show, Don't Tell", "Sensory Details", "Kid Dialogue", "Positive Moral", "World Seeds", "Category Flavor: Furry Friends"],
    "Space Adventure": ["Clear Arc (B-M-E)", "Rule of Three", "Sensory Details", "Kid Dialogue", "Positive Moral", "Figurative Light", "Category Flavor: Space Adventure"],
    "Boo!": ["Clear Arc (B-M-E)", "Safe Stakes", "Humor & Surprise", "Sensory Details", "Kid Dialogue", "Positive Moral", "Category Flavor: Boo!"],
}

def _choose_techniques_for(category: str) -> List[str]:
    base = CATEGORY_TECHNIQUE_MAP.get(category, ["Clear Arc (B-M-E)", "Show, Don't Tell", "Positive Moral"])
    picks = base[:]
    random.shuffle(picks)
    for g in ["Sensory Details", "Kid Dialogue", "Vocabulary Ceiling"]:
        if g not in picks:
            picks.append(g)
    return picks[:7]

def detect_category(user_input: str) -> str:
    mapping = {
        "magic_adventure": ["wizard", "magic", "castle", "fairy", "dragon"],
        "epic_quest": ["journey", "quest", "explore", "map", "treasure"],
        "mystery": ["mystery", "secret", "clue", "detective", "case"],
        "funny": ["funny", "silly", "laugh", "joke", "goofy"],
        "friends_and_family": ["family", "friend", "home", "siblings", "school"],
        "furry_friends": ["cat", "dog", "rabbit", "animal", "pet"],
        "space_adventure": ["space", "planet", "rocket", "alien", "moon"],
        "boo": ["ghost", "spooky", "monster", "witch", "boo"],
    }
    lower = (user_input or "").lower()
    for key, words in mapping.items():
        if any(w in lower for w in words):
            return CATEGORIES[key]
    return random.choice(CATEGORIES_PUBLIC)

def determine_age_bracket(age_bracket: str) -> str:
    ab = (age_bracket or "middle").strip().lower()
    if ab.startswith("y"): return "young"
    if ab.startswith("o"): return "older"
    return "middle"

def call_model(messages, temperature=0.7, max_tokens=1600) -> str:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

def build_storyteller_prompt(user_request: str, category: str, age_bracket: str) -> list:
    chosen = _choose_techniques_for(category)
    technique_lines = "\n".join([f"- {TECHNIQUES[t]}" if t in TECHNIQUES else f"- {t}" for t in chosen])

    guidelines = f"""
You are a veteran children's storyteller writing for ages 5–10 (age bracket: {age_bracket}).
{_insp_storyteller()}

### Creative brief
- Category/Style: {category}
- Reader: a child in the {age_bracket} bracket (keep language accessible; roughly Grade 2–4 reading ease).
- Length target: 600–900 words (never under 500 words). Prefer elaboration over brevity.

### Safety & tone
- Absolutely no gore, sexual content, bullying, or mature themes.
- Conflict is gentle and safe; end with warmth, reassurance, and hope.

### Story craft to apply
{technique_lines}

### Structural beats (keep them clear but graceful)
1) Beginning — cozy setup: who (kid-friendly names), where (grounding details), what they care about.
2) Middle — a small challenge or mystery; 2–3 light beats or tries; playful tension; show emotions via action and dialogue.
3) Ending — a kind resolution; a positive, natural moral without preaching.

### Language & style
- Prefer short sentences and lively verbs. Keep vocabulary simple; explain rare words in context.
- Use sensory details sparingly and clearly.
- Add short dialogue lines with clear attributions.
- Use light humor or surprise where appropriate to the category.
- Avoid repeated phrases and clichés.

### Output rules
- Do NOT include an outline or section headers—write a single continuous story.
- Do NOT reference external sources directly.
- Do NOT break character as a storyteller.

Now write the story that responds to the child's request below while honoring all guidance.
""".strip()

    return [
        {"role": "system", "content": guidelines},
        {"role": "user", "content": (user_request or "Tell me a fun and imaginative story for a child.")},
    ]

def build_judge_prompt(story: str, user_feedback: Optional[str] = None) -> list:
    originality_line = _insp_judge()
    revision_brief = f"""
You are a careful children's story editor (ages 5–10). Revise the story to improve craft and safety.
Maintain originality; you may rewrite, expand, or trim lines to meet goals.

### Editing checklist (apply all as needed)
- Structure & pacing: clear beginning–middle–end; smooth transitions; 2–3 light middle beats.
- Length: aim 600–900 words. If <500, expand with action, dialogue, and sensory detail (not filler). If >950, tighten gently.
- Age-appropriate language: roughly Grade 2–4; explain rare words in-context.
- Dialogue: short, lively exchanges; clear speakers.
- Sensory details: light, concrete anchors (sound, color, texture, smell).
- Moral & warmth: gentle, positive takeaway woven naturally; no preaching.
- Category fidelity: keep style aligned with its category.
- Consistency: names/POV stable; remove contradictions.
- Repetition & clichés: replace with fresh lines.
- Safety: nothing too scary/mature; reassuring ending.
- {originality_line}

### Output rules
- Return the **revised full story** only (no commentary).
- Preserve the child-friendly tone; never break the fourth wall.
""".strip()
    if user_feedback:
        revision_brief += f"\n\n### Additional user feedback to apply now\n- {user_feedback.strip()}\n"

    return [
        {"role": "system", "content": revision_brief},
        {"role": "user", "content": story},
    ]

def generate_story_api(user_request: str, age_bracket: str, category: Optional[str] = None) -> Tuple[str, str]:
    chosen_category = category or detect_category(user_request)
    ab = determine_age_bracket(age_bracket)
    draft = call_model(build_storyteller_prompt(user_request, chosen_category, ab), temperature=0.85, max_tokens=1600)
    improved = call_model(build_judge_prompt(draft), temperature=0.6, max_tokens=1600)
    return improved, chosen_category

def revise_story_api(current_story: str, user_feedback: str) -> str:
    revised = call_model(build_judge_prompt(current_story, user_feedback=user_feedback), temperature=0.6, max_tokens=1600)
    return revised
