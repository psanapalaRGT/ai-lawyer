# NyayaSaathi - India online-shopping complaint assistant (prototype)

**Kuku AI Generalist Assignment: Problem 2 - Build an AI Lawyer.**

A narrowly scoped, conversational consumer-help prototype. It takes a messy account of an online shopping issue, extracts a case card, identifies evidence/missing facts, suggests the *official* consumer-grievance route, and drafts a polite letter for the user to edit.

## Run now, no API key (working offline)

```bash
python demo.py "I ordered headphones from ShopKart for Rs 2,499. Order ID SK12345. It never arrived."
python run_cases.py
python -m unittest discover -s tests -v
```

This is a **rules-only fallback**, not AI inference. It is intentionally fully runnable offline; the real AI mode is configured below. Run the included test cases to reproduce the `raw_outputs/` folder. T08 is deliberately a failing classification test, documented as evidence of a limitation. Both modes use the same source-anchored output/safety layer.

## Run interactive UI

```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter a narrative, inspect the extracted facts, next steps, source links, and generated editable complaint draft. The prototype does not submit complaints.

## Run with a free local AI model (optional)

Install Ollama and download a compatible model:

```bash
ollama pull llama3.2:3b
ollama serve
# In another terminal, in this project directory:
python demo.py --ai "I ordered headphones from ShopKart. The package never arrived."
```

Ollama may already be running; in that case you don't need another `ollama serve`. In Streamlit, turn on **Use local/external AI for fact extraction**. The default adapter uses `http://localhost:11434/v1`, `llama3.2:3b`. Change `MODEL_BASE_URL`, `MODEL_NAME`, `MODEL_API_KEY` for another OpenAI-compatible endpoint. For example:

```bash
export MODEL_BASE_URL=http://localhost:11434/v1
export MODEL_NAME=llama3.2:3b
export MODEL_API_KEY=ollama
```

**Privacy:** local model inference keeps submitted narratives local; external endpoints receive the text you provide, so remove personal IDs/financial details first. The app does not intentionally log or persist chat content; downloaded case files belong to the user.

## Design choices

1. **AI's role:** translate a messy statement into structured fields with literal, auditable evidence spans. The adapter rejects facts that cannot be matched to an exact quote in the user input. Its category suggestion is bounded to a small enum; it cannot override a safety-sensitive rule-based classification.
2. **Code's role:** route only supported cases; create questions, checklists, next steps, and drafts using fixed templates. Unknown fields appear as square-bracket placeholders, not invented values.
3. **Grounding:** curated, publicly accessible government references in `knowledge.py`. The model is never asked to supply legal sections or court precedents. No invented eligibility, deadlines, or predictions.
4. **Human-in-the-loop:** user reviews the draft, fills gaps, and chooses whether to contact seller, NCH or a lawyer. Formal court filing remains outside scope.
5. **Scale:** source registry and templates are versioned once; add categories with their own verified source sets. Batch handling can be stateless. A smaller extraction model reduces per-case cost; human review is reserved for ambiguous/high-risk cases.

## Limits / honest failures

- Tested raw outputs in this package are **offline rules-only**. We did not execute the optional Ollama model in this environment. Do not describe baseline runs as LLM runs.
- Rules detect only a narrow range of English and a couple of Hindi/Telugu phrases. Most multilingual input requires model mode and human review.
- Dates, product names and sellers may be missed or extracted poorly (e.g. T02 mentions BuyNow, but offline extraction does not capture it); case facts must be confirmed by the user. A seller name that looks like a preposition phrase could be wrong.
- The app doesn't verify documents, user identity, merchant identities, legal eligibility, limitation periods, jurisdiction, or uploaded evidence.
- Some disputes (salary, landlord, threats, safety risks) are deliberately routed away instead of producing inappropriate legal paperwork.
- Official links and procedures should be refreshed before wider deployment; reviewed 2026-11-06.

## Evidence of quality

Run `python run_cases.py` to reproduce **eight raw case outputs** and the summary. Tests exercise non-delivery, delayed refund, missing facts/prompt injection, out-of-scope requests, urgency Hindi text, and one deliberately retained known failure. Use `python -m unittest discover -s tests -v` for regression checks. Classification alone is not sufficient: verify that the draft contains no invented statute or order number, and that unsafe cases trigger escalation.

## Files to submit

- `SOLUTION_DOC.pdf` (two pages)
- A **publicly accessible** GitHub repository or deployed Streamlit link (the zip is not a public deployment)
- `raw_outputs/` folder from the above test run
- Optional, recommended: record your own <=3-minute walkthrough demonstrating a new input and one failure case.

## Official grounding sources

See `knowledge.py` and `sources.md` for official links and statements supported by each source.
