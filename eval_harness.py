import os
import openai
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

# ==== Config ====

# Load OpenAI API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set. Please define it in your .env file.")

openai.api_key = api_key

MODEL_NAME = "gpt-4.1"
TEMPERATURE = 0.2
PROMPT_TEMPLATE_PATH = "prompts/eval_prompt.txt"
OUTPUT_CSV = "results/eval_scores.csv"

# Evaluation data pairs (transcript, generated note)
DATA_PAIRS = [
    ("data/intake_session_transcript.txt", "data/intake_note.txt"),
    ("data/progress_session_transcript.txt", "data/progress_note.txt"),
]


# ==== Prompt Handling ====

def load_prompt_template(path):
    """
    Load the base evaluation prompt from file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_full_prompt(base_prompt, transcript, note):
    """
    Construct full prompt by injecting transcript and generated note.
    """
    return (
        f"{base_prompt.strip()}\n\n"
        f"=== SESSION TRANSCRIPT ===\n{transcript.strip()}\n\n"
        f"=== GENERATED NOTE ===\n{note.strip()}"
    )


# ==== GPT Interaction ====

def query_openai(prompt, model=MODEL_NAME, temperature=TEMPERATURE):
    """
    Submit prompt to OpenAI's ChatCompletion API and return the response.
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


# ==== Score Parsing ====

def parse_scores(response):
    """
    Parse GPT response to extract 3 evaluation scores from fixed format.
    Expected format (one per line):
    Clarity & Structure: <score>/5 – <reason>
    Clinical Accuracy & Appropriateness: <score>/5 – <reason>
    Tone & Professionalism: <score>/5 – <reason>
    """
    scores = {"clarity_score": None, "accuracy_score": None, "tone_score": None}
    for line in response.strip().splitlines():
        if "Clarity" in line:
            scores["clarity_score"] = int(line.split(":")[1].split("/")[0].strip())
        elif "Accuracy" in line or "Appropriateness" in line:
            scores["accuracy_score"] = int(line.split(":")[1].split("/")[0].strip())
        elif "Tone" in line:
            scores["tone_score"] = int(line.split(":")[1].split("/")[0].strip())
    return scores


# ==== Evaluation Loop ====

def evaluate_all():
    """
    Run evaluation over all transcript-note pairs and save results to CSV.
    """
    base_prompt = load_prompt_template(PROMPT_TEMPLATE_PATH)
    all_results = []

    for transcript_path, note_path in tqdm(DATA_PAIRS, desc="Evaluating notes"):
        with open(transcript_path, "r", encoding="utf-8") as f1, open(note_path, "r", encoding="utf-8") as f2:
            transcript = f1.read()
            note = f2.read()

        prompt = build_full_prompt(base_prompt, transcript, note)
        response = query_openai(prompt)
        scores = parse_scores(response)

        scores.update({
            "transcript_file": os.path.basename(transcript_path),
            "note_file": os.path.basename(note_path),
            "raw_response": response  # Optional: keep for audit/debug
        })
        all_results.append(scores)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
    print(f"Evaluation complete. Results saved to: {OUTPUT_CSV}")


# ==== Script Entry Point ====

if __name__ == "__main__":
    evaluate_all()
