# Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io with GitHub account `psanapalaRGT` and connect the GitHub account when prompted.
2. Click **Create app** and choose **Yup, I have an app**.
3. Set repository to `psanapalaRGT/ai-lawyer`, branch `main`, main file path `app.py`.
4. Optional app URL: `nyayasaathi-ai-lawyer` (only if not taken).
5. Click **Deploy**. The free rules-only mode works without secrets or API keys.
6. Enter a consumer refund scenario; use the download buttons to verify output.

The **Use local/external AI** toggle must stay OFF on Streamlit Community Cloud unless an external OpenAI-compatible LLM API has been configured. An Ollama server on `localhost:11434` on a user's laptop cannot be reached from Streamlit Community Cloud. Any API secret belongs in Streamlit Secrets, not GitHub. Run both rules and model modes yourself before making claims about model performance.

Submit separately to Kuku: the two-page `SOLUTION_DOC.pdf`, the GitHub/Streamlit link, and the `raw_outputs` folder. Do not publish Kuku's confidential screenplay input pack.
