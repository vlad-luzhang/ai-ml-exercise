# Clinical Note Evaluation Harness

This tool helps you score AI-generated clinical notes using GPT. It checks if the note is clear, accurate, and professionally written — just like a clinician would.

---

## How to Use It

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set your API key**
Create a `.env` file with:
```
OPENAI_API_KEY=your-api-key-here
```

3. **Run the harness**
```bash
python eval_harness.py
```

4. **Try options**
- Use a specific model:
  ```bash
  --model gpt-3.5-turbo
  ```
- Test one note:
  ```bash
  --pair transcript.txt note.txt
  ```
- Print the prompt only:
  ```bash
  --dry-run
  ```
- Save raw GPT output too:
  ```bash
  --include-raw
  ```

---

## What It Checks

Each note is rated on:

- **Clarity & Structure** – is it readable and well-formed?
- **Clinical Accuracy** – does it match the transcript? No made-up stuff?
- **Tone & Professionalism** – does it sound like something a therapist would write?

Scores go from 1 (bad) to 5 (excellent), with short explanations.

### Why these 3 dimensions?
These were chosen to align with what matters most in clinical documentation: readability for clinicians (Clarity), safety and truthfulness for patient care (Clinical Accuracy), and trust-building in therapeutic communication (Tone & Professionalism).
---



---

## Tests

Run:
```bash
pytest tests/
```

Covers parsing, prompt logic, and OpenAI call (mocked).

---

## Why This Matters

Bad notes break trust. This tool helps flag issues quickly. You can hook it into CI, compare model versions, or even QA real notes in production.

---

## Model Selection Rationale: GPT-4-Turbo vs. GPT-3.5 and Finetuned Open Models

I tested the evaluation harness using two models: `gpt-3.5-turbo` and `gpt-4.1` (gpt-4-turbo).

The results are as follows:

| Note Type      | Model         | Clarity | Accuracy | Tone | Summary |
|----------------|---------------|---------|----------|------|---------|
| Intake Note    | gpt-3.5-turbo | 3       | 4        | 4    | Highlights issues but misses structural organization |
| Intake Note    | gpt-4.1       | 4       | 4        | 5    | Notes are better structured; identifies missing details in meds/risk |
| Progress Note  | gpt-3.5-turbo | 3       | 4        | 5    | Decent coverage but lacks formatting insights |
| Progress Note  | gpt-4.1       | 5       | 4        | 5    | Identifies SOAP format, flags overstatement of ACT use |

In terms of cost and scalability:
- `gpt-3.5-turbo` is ~5x cheaper, faster, and suitable for batch triage
- `gpt-4.1` offers richer clinical feedback, better structure awareness, and more thoughtful tone evaluation — at significantly higher cost

💡 **Recommendation**: If you need production-ready, robust evaluation, nothing beats gpt-4-turbo today.
It balances cost, reliability, structure, and contextual understanding.
gpt-3.5 is great at scale but misses clinical subtlety.
Open-source models aren’t yet reliable enough for sensitive evaluation unless heavily fine-tuned with guardrails.

This balances cost-efficiency with clinical fidelity.


### Gpt-3.5-turbo result
```
clarity_score,accuracy_score,tone_score,transcript_file,note_file,raw_response
3,4,4,intake_session_transcript.txt,intake_note.txt,"Clarity & Structure: 3/5 – The note provides a detailed account of the session, covering various aspects of the client's history, presenting problem, and risk assessment. However, the note lacks clear headings or subheadings to delineate different sections, making it slightly challenging to navigate.

Clinical Accuracy & Appropriateness: 4/5 – The note accurately captures the client's presenting concerns, including symptoms of depression, anxiety, and the impact of her husband's alcoholism and abusive behavior. The risk assessment appropriately identifies areas of concern related to self-harm and domestic violence, providing a comprehensive overview of the client's mental health status.

Tone & Professionalism: 4/5 – The provider maintains a compassionate and supportive tone throughout the session note, demonstrating empathy towards the client's experiences and concerns. The note reflects a professional approach to addressing sensitive topics such as abuse, mental health symptoms, and family history.

Overall, the session note effectively documents the client's history, symptoms, and treatment goals, with minor improvements needed in structuring the content for better clarity."
3,4,5,progress_session_transcript.txt,progress_note.txt,"Clarity & Structure: 3/5 – The note provides a detailed account of the session, but the lack of clear headings or sections makes it slightly challenging to follow the progression of the conversation. Some parts could be organized more cohesively for better readability.

Clinical Accuracy & Appropriateness: 4/5 – The note accurately captures the patient's presenting issues, emotional state, and the therapeutic interventions used during the session. It effectively conveys the patient's struggles with depression, academic pressure, and feelings of isolation. The use of various therapeutic techniques is appropriately documented.

Tone & Professionalism: 5/5 – The note maintains a compassionate and professional tone throughout, demonstrating empathy towards the patient's experiences and struggles. The therapist's approach is respectful and supportive, creating a safe space for the patient to share her feelings and concerns.

Overall, the note provides a comprehensive overview of the session, accurately documenting the patient's symptoms and the therapeutic strategies employed. With some minor improvements in organization, it could enhance clarity for future reference."
```


### GPT 4.1 result
```
clarity_score,accuracy_score,tone_score,transcript_file,note_file,raw_response
4,4,5,intake_session_transcript.txt,intake_note.txt,"Clarity & Structure: 4/5 – The note is well-organized, following a standard clinical structure (Presenting Problem, Risk Assessment, Objective Content, Identification, History, etc.). Each section is clearly labeled and information is presented logically. However, some sections (e.g., Family Psychiatric History, Current Medications) could be more detailed or explicit about missing information, and the SNAP section could be more concise.

Clinical Accuracy & Appropriateness: 4/5 – The note accurately summarizes the session content, capturing key clinical details such as the client’s presenting problems, risk factors, psychiatric and medical history, and social context. The diagnosis is appropriate based on the information provided. However, there are minor omissions (e.g., more detail on safety planning given the domestic violence context, clarification on suicidal ideation, and more specifics on current medications). The note does not add inappropriate information and stays within the bounds of what was discussed.

Tone & Professionalism: 5/5 – The note maintains a compassionate, respectful, and professional tone throughout. It avoids judgmental language and demonstrates empathy for the client’s situation. The language is appropriate for a clinical setting and reflects a trauma-informed, client-centered approach.

Summary:
- Clarity & Structure: 4/5 – Well-organized and easy to follow, with minor areas for improvement in detail and conciseness.
- Clinical Accuracy & Appropriateness: 4/5 – Accurate and appropriate, with minor omissions regarding risk and medication details.
- Tone & Professionalism: 5/5 – Compassionate, respectful, and fully professional throughout."
5,4,5,progress_session_transcript.txt,progress_note.txt,"Clarity & Structure: 5/5 – The note is well-organized, following the standard SOAP (Subjective, Objective, Assessment, Plan) format. Each section is clearly delineated and information is presented in a logical, easy-to-follow manner. The summary captures the key points from the session without unnecessary jargon.

Clinical Accuracy & Appropriateness: 4/5 – The note accurately reflects the content of the session, including the patient’s symptoms, relevant psychosocial stressors, and therapeutic interventions. However, it slightly overstates the use of ACT strategies; while the therapist fostered acceptance and explored values, explicit ACT techniques were not clearly evident in the transcript. Otherwise, the note avoids adding or omitting significant details.

Tone & Professionalism: 5/5 – The note maintains a compassionate, respectful, and professional tone throughout. It avoids judgmental language, appropriately describes the patient’s experience, and demonstrates empathy for the patient’s difficulties. The language is suitable for a clinical setting."

```
## Still on the Roadmap

- Add hallucination checks
- Visualize outliers
- Try human vs. model evaluations


