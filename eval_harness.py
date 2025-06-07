import os
import argparse
import pandas as pd
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from tqdm import tqdm

# ==== Configuration ====

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set. Please define it in your .env file.")

client = OpenAI()

DEFAULT_MODEL = "gpt-4.1"
DEFAULT_TEMPERATURE = 0.2
PROMPT_TEMPLATE_PATH = "prompts/eval_prompt.txt"
DEFAULT_OUTPUT_CSV = "results/eval_scores.csv"
DEFAULT_DATA_PAIRS = [
    ("data/intake_session_transcript.txt", "data/intake_note.txt"),
    ("data/progress_session_transcript.txt", "data/progress_note.txt"),
]


# ==== CLI Arguments ====

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate clinical notes using an OpenAI LLM")

    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model to use (e.g. gpt-3.5-turbo)")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_CSV, help="Path to save evaluation results")
    parser.add_argument("--include-raw", action="store_true", help="Include raw GPT response in the output CSV")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt and skip GPT call")
    parser.add_argument("--pair", nargs=2, metavar=("TRANSCRIPT", "NOTE"), help="Evaluate a single file pair")

    return parser.parse_args()


# ==== Prompt Handling ====

def load_prompt_template(path: str) -> str:
    """Load the base evaluation prompt from file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt template not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_full_prompt(base_prompt: str, transcript: str, note: str) -> str:
    """Inject transcript and note into the base evaluation template."""
    return (
        f"{base_prompt.strip()}\n\n"
        f"=== SESSION TRANSCRIPT ===\n{transcript.strip()}\n\n"
        f"=== GENERATED NOTE ===\n{note.strip()}"
    )


# ==== GPT Interaction ====

def query_openai(prompt: str, model: str, temperature: float = DEFAULT_TEMPERATURE) -> str:
    """Submit prompt to OpenAI's chat completions API and return the response content."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a clinical documentation evaluator."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")


# ==== Score Parsing ====

def parse_scores(response: str) -> dict:
    """
    Parse GPT response to extract 3 evaluation scores from fixed format.
    Expected format (one per line):
        Clarity & Structure: <score>/5 – <reason>
        Clinical Accuracy & Appropriateness: <score>/5 – <reason>
        Tone & Professionalism: <score>/5 – <reason>
    """
    scores = {
        "clarity_score": None,
        "accuracy_score": None,
        "tone_score": None,
    }

    for line in response.strip().splitlines():
        if "Clarity" in line:
            scores["clarity_score"] = int(line.split(":")[1].split("/")[0].strip())
        elif "Accuracy" in line or "Appropriateness" in line:
            scores["accuracy_score"] = int(line.split(":")[1].split("/")[0].strip())
        elif "Tone" in line:
            scores["tone_score"] = int(line.split(":")[1].split("/")[0].strip())

    return scores


# ==== Evaluation Loop ====

def evaluate_all(args) -> None:
    base_prompt = load_prompt_template(PROMPT_TEMPLATE_PATH)
    results = []

    # Use custom or default file pairs
    pairs = [tuple(args.pair)] if args.pair else DEFAULT_DATA_PAIRS

    for transcript_path, note_path in tqdm(pairs, desc="Evaluating notes"):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f1, open(note_path, "r", encoding="utf-8") as f2:
                transcript = f1.read()
                note = f2.read()
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            continue

        prompt = build_full_prompt(base_prompt, transcript, note)

        if args.dry_run:
            print(f"DRY RUN: Prompt for {note_path}:\n")
            print(prompt)
            continue

        try:
            response = query_openai(prompt, model=args.model)
        except RuntimeError as e:
            print(f"Skipping {note_path} due to API error:\n{e}")
            continue

        scores = parse_scores(response)

        if any(score is None for score in scores.values()):
            print(f"Incomplete scores for {note_path}. Raw response:\n{response}")
            continue

        for k, v in scores.items():
            if not (1 <= v <= 5):
                print(f"Invalid score: {k} = {v}. Skipping.")
                continue

        scores.update({
            "transcript_file": os.path.basename(transcript_path),
            "note_file": os.path.basename(note_path),
        })

        if args.include_raw:
            scores["raw_response"] = response

        results.append(scores)

    if not results:
        print("No valid results to write.")
        return

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    pd.DataFrame(results).to_csv(args.output, index=False)
    print(f"Evaluation complete. Results saved to: {args.output}")


# ==== Script Entry Point ====

if __name__ == "__main__":
    args = parse_args()
    evaluate_all(args)
