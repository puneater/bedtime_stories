import os
from openai import OpenAI
import random
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# --- Category Definitions ---
CATEGORIES = {
    "magic_adventure": "Magic Adventure",
    "epic_quest": "Epic Quest",
    "mystery": "Mystery",
    "funny": "Funny",
    "friends_and_family": "Friends and Family",
    "furry_friends": "Furry Friends",
    "space_adventure": "Space Adventure",
    "boo": "Boo!"
}

# --- External Inspiration Resources ---
INSPIRATION_SITES = [
    "https://www.storyberries.com",
    "https://www.sleepystories.net",
    "https://www.freechildrenstories.com",
    "https://www.bedtimestory.ai"
]

# --- Utility Functions ---
def detect_category(user_input: str) -> str:
    """Infer category based on keywords in user input."""
    mapping = {
        "magic_adventure": ["wizard", "magic", "castle", "fairy", "dragon"],
        "epic_quest": ["journey", "quest", "explore", "map", "treasure"],
        "mystery": ["mystery", "secret", "clue", "detective", "case"],
        "funny": ["funny", "silly", "laugh", "joke", "goofy"],
        "friends_and_family": ["family", "friend", "home", "siblings", "school"],
        "furry_friends": ["cat", "dog", "rabbit", "animal", "pet"],
        "space_adventure": ["space", "planet", "rocket", "alien", "moon"],
        "boo": ["ghost", "spooky", "monster", "witch", "boo"]
    }
    input_lower = user_input.lower()
    for cat, keywords in mapping.items():
        if any(word in input_lower for word in keywords):
            return CATEGORIES[cat]
    return random.choice(list(CATEGORIES.values()))


def determine_age_bracket(age: int) -> str:
    if age <= 6:
        return "young"
    elif age <= 8:
        return "middle"
    else:
        return "older"


def call_model(messages, temperature=0.7, max_tokens=1600):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

# --- Story Generation Logic ---
def build_storyteller_prompt(user_request: str, category: str, age_bracket: str) -> list:
    system_message = f"""
You are a creative children's storyteller. 
Use inspiration from well-written stories on trusted children's sites like: {', '.join(INSPIRATION_SITES)}.

The child is in the {age_bracket} age bracket (5-10 years old).
Category: {category}

Guidelines:
- Write a story with a clear beginning, middle, and happy ending.
- Include a gentle conflict or challenge suitable for a child.
- Use age-appropriate, vivid, and engaging language.
- Include positive values or a small moral.
- Aim for 500-1000 words. Prioritize elaboration over brevity.
- Keep it safe and appropriate: no scary, violent, or mature content.
- Be imaginative, unique, and draw subtle inspiration from the mentioned sources without copying.
    """
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_request}
    ]


def build_judge_prompt(story: str, user_feedback: Optional[str] = None) -> list:
    critique_instruction = f"""
You are a children's story judge. Improve this story by checking for:
- Structure (beginning-middle-end)
- Clarity and engagement
- Age-appropriate language
- Gentle tone and moral
- Remove anything inappropriate
- Ensure it's closer to 500-1000 words if too short
- Take creative inspiration from sites like: {', '.join(INSPIRATION_SITES)}
"""
    if user_feedback:
        critique_instruction += f"\nAlso apply this user feedback: {user_feedback}\n"
    return [
        {"role": "system", "content": critique_instruction},
        {"role": "user", "content": story}
    ]


def generate_story(user_request: str, age: int, category: Optional[str] = None) -> str:
    chosen_category = category or detect_category(user_request)
    age_bracket = determine_age_bracket(age)
    storyteller_prompt = build_storyteller_prompt(user_request, chosen_category, age_bracket)
    raw_story = call_model(storyteller_prompt, temperature=0.85, max_tokens=1600)
    judge_prompt = build_judge_prompt(raw_story)
    final_story = call_model(judge_prompt, temperature=0.65, max_tokens=1600)
    return final_story


def revise_story_from_interrupt(current_story: str, interrupt_point: str, user_feedback: str) -> str:
    revision_prompt = build_judge_prompt(current_story, user_feedback=user_feedback)
    revised_story = call_model(revision_prompt, temperature=0.65, max_tokens=1600)
    return revised_story


# --- Main CLI entry ---
def main():
    age = int(input("Child's age (5-10): "))
    mode = input("Choose 'surprise', 'category', or 'custom': ").strip().lower()

    if mode == "surprise":
        request = "Tell me a fun and imaginative story for a child."
        category = random.choice(list(CATEGORIES.values()))
    elif mode == "category":
        for key, val in CATEGORIES.items():
            print(f"- {val}")
        category = input("Enter a story category from above: ")
        request = input("What should the story be about? (short prompt): ")
    else:
        request = input("What kind of story do you want to hear? ")
        category = None

    final_story = generate_story(request, age, category)
    print("\nHere is your story:\n")
    print(final_story)


if __name__ == "__main__":
    main()
