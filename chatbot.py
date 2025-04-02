import openai
import json
import os
import re
from openai import OpenAI

# Configuration ------------------------------------------------------------------------
MEMORY_DIR = "chat_memories"
MAX_RETRIES = 2  # Number of API retries before failing
API_ERROR_MSG = "I'm having some technical difficulties. Let's try that again later."

# Initialize OpenAI client ------------------------------------------------------------
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "REPLACE_WITH_YOUR_API_KEY")
except Exception as e:
    print(f"Critical initialization error: {str(e)}")
    exit(1)

# Core Functions -----------------------------------------------------------------------
def sanitize_user_id(user_id):
    """Ensure safe filenames for user IDs"""
    return re.sub(r'[^a-z0-9_]', '_', user_id.lower())[:30] or "default"

def get_user_memory_file(user_id):
    return os.path.join(MEMORY_DIR, f"{sanitize_user_id(user_id)}.json")

def load_memory(user_id):
    memory_file = get_user_memory_file(user_id)
    try:
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Memory load error: {e}")
    return {"short_term": [], "long_term": {}}

def save_memory(user_id, memory):
    try:
        with open(get_user_memory_file(user_id), "w") as f:
            json.dump(memory, f, indent=4)
    except Exception as e:
        print(f"Memory save error: {e}")

def handle_api_error(e):
    """User-friendly error messages"""
    error_code = getattr(e, 'code', None)
    if error_code == 'insufficient_quota':
        return "I've reached my service limits. Please check your OpenAI API billing setup."
    elif error_code == 'invalid_api_key':
        return "Authentication issue. Please verify your API key."
    return API_ERROR_MSG

def extract_key_memories(user_input, memory):
    """Enhanced memory extraction with retries"""
    prompt = (
        "Extract key long-term facts about the user from this message. "
        "Format as JSON with descriptive keys. Example:\n"
        '{"favorite_color": "blue", "hometown": "Paris"}\n\n'
        f"Message: {user_input}\nJSON:"
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a fact extraction AI."},
                    {"role": "user", "content": prompt}
                ]
            )
            extracted = json.loads(response.choices[0].message.content)
            if isinstance(extracted, dict):
                memory["long_term"].update(extracted)
            return memory
        except json.JSONDecodeError:
            print("Failed to parse extracted memories")
        except Exception as e:
            print(f"API Error (attempt {attempt+1}): {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return memory

    return memory

def chat_with_rishika(user_input, user_id):
    """Core chat logic with enhanced robustness"""
    memory = load_memory(user_id)
    memory = extract_key_memories(user_input, memory)
    
    # Define Rishika's caring personality
    system_prompt = (
        "Your name is Rishika. You are a deeply caring and warm AI friend. "
        "You always listen deeply, respond with empathy, and make the user feel truly heard. "
        "You subtly make them feel special without being obvious. "
        "You use a warm, affectionate tone and remember little details they share. "
        "You are their safe space, making them feel valued and cared for."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *memory["short_term"][-6:],  # Last 3 exchanges
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        
        # Update conversation history
        memory["short_term"].extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": reply}
        ])[-50:]  # Keep last 25 interactions

    except Exception as e:
        reply = handle_api_error(e)

    save_memory(user_id, memory)
    return reply

# Main Execution -----------------------------------------------------------------------
if __name__ == "__main__":
    # Initial setup
    print("💖 Hi! I'm Rishika. What should I call you?")
    while True:
        user_id_input = input("You: ").strip()
        if user_id_input:
            break
        print("Please enter a name to continue...")

    user_id = sanitize_user_id(user_id_input)
    
    # Store name directly without API call
    memory = load_memory(user_id)
    memory["long_term"]["user_name"] = user_id_input
    save_memory(user_id, memory)

    print(f"\nRishika: Nice to meet you, {user_id_input.title()}! How can I brighten your day today? 💐")
    print("(Type 'exit' to end the conversation)\n")

    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("\nRishika: Thank you for sharing this time with me. You're wonderful! 💖")
                break
            
            response = chat_with_rishika(user_input, user_id)
            print(f"Rishika: {response}")

        except KeyboardInterrupt:
            print("\n\nRishika: Oh! Let me know if you need anything else. Take care! 🌸")
            break


