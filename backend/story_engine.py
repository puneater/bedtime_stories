import os
import random
from typing import Optional, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Categories (public labels used by UI) ---
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

# Inspiration (static for now; scraping layer can be added later)
INSPIRATION_SITES = [
    "https://www.storyberries.com",
    "https://www.sleepystories.net",
    "https://www.freechildrenstories.com",
    "https://www.bedtimestory.ai",
]

# OpenAI client (SDK >= 1.0.0)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


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
    """
    Normalize to one of: 'young' (5-6), 'middle' (7-8), 'older' (9-10).
    Frontend passes these strings; this function just sanitizes.
    """
    ab = (age_bracket or "middle").strip().lower()
    if ab.startswith("y"):
        return "young"
    if ab.startswith("o"):
        return "older"
    return "middle"


def call_model(messages, temperature=0.7, max_tokens=1600) -> str:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# --- Prompt Builders ---

def build_storyteller_prompt(user_request: str, category: str, age_bracket: str) -> list:
    guidelines = f"""
You are a creative children's storyteller for ages 5-10 (age bracket: {age_bracket}).
Write a unique story inspired by—but not copying—public children's story sites: {', '.join(INSPIRATION_SITES)}.

Rules:
- Clear beginning, middle, and happy ending.
- Gentle, age-appropriate conflict and satisfying resolution.
- Positive value or small moral woven into the plot (show, don't tell).
- Use vivid, fun language and dialogue suitable for a {age_bracket} child.
- Aim for 500-1000 words. Prioritize elaboration over brevity.
- Absolutely no gore, sexual content, or mature themes.
- Category style: {category}.
"""
    return [
        {"role": "system", "content": guidelines},
        {"role": "user", "content": user_request or "Tell me a fun and imaginative story for a child."},
    ]


def build_judge_prompt(story: str, user_feedback: Optional[str] = None) -> list:
    instr = f"""
You are a children's story judge-editor. Improve the story by:
- Ensuring a clear arc (beginning-middle-end), engaging pacing, and coherent plot.
- Expanding toward ~500-1000 words if the story is too short (prefer elaboration).
- Strengthening character voice and gentle humor; add kid-friendly dialogue where helpful.
- Preserving originality while drawing *subtle* inspiration from: {', '.join(INSPIRATION_SITES)}.
- Verifying tone and vocabulary are age-appropriate; remove anything inappropriate.
- Keep the user's intent and any feedback.
If the story is already strong, polish lightly.
"""
    if user_feedback:
        instr += f"\nUser feedback to apply: {user_feedback}\n"
    return [
        {"role": "system", "content": instr},
        {"role": "user", "content": story},
    ]


# --- Public API helpers used by Flask ---

def generate_story_api(user_request: str, age_bracket: str, category: Optional[str] = None) -> Tuple[str, str]:
    chosen_category = category or detect_category(user_request)
    ab = determine_age_bracket(age_bracket)
    draft = call_model(
        build_storyteller_prompt(user_request, chosen_category, ab),
        temperature=0.85,
        max_tokens=1600,
    )
    improved = call_model(
        build_judge_prompt(draft),
        temperature=0.65,
        max_tokens=1600,
    )
    return improved, chosen_category


def revise_story_api(current_story: str, user_feedback: str) -> str:
    revised = call_model(
        build_judge_prompt(current_story, user_feedback=user_feedback),
        temperature=0.65,
        max_tokens=1600,
    )
    return revised
