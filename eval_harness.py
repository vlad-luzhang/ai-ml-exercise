import os
import openai
from dotenv import load_dotenv

# ==== Config ====
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-4"
TEMPERATURE = 0.2
PROMPT_TEMPLATE_PATH = "prompts/eval_prompt.txt"

# ==== Prompt Handling ====

def load_prompt_template(path):
    """
    Load the base prompt from file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_full_prompt(base_prompt, transcript, note):
    """
    Inject transcript and note into the evaluation template.
    """
    return (
        f"{base_prompt.strip()}\n\n"
        f"=== SESSION TRANSCRIPT ===\n{transcript.strip()}\n\n"
        f"=== GENERATED NOTE ===\n{note.strip()}"
    )

# ==== GPT Interaction ====

def query_openai(prompt, model=MODEL_NAME, temperature=TEMPERATURE):
    """
    Call the OpenAI API with the given prompt and return the LLM response.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a clinical documentation evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    return response["choices"][0]["message"]["content"]
