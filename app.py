"""Streamlit UI: streamlit run app.py"""
import json
import os
import streamlit as st
from engine import analyze

st.set_page_config(page_title="NyayaSaathi | Consumer Complaint Assistant", page_icon="⚖️", layout="centered")
st.title("⚖️ NyayaSaathi")
st.caption("Online-shopping refund complaint assistant | India | Prototype")
st.info("This pilot covers online purchases, non-delivery and refund problems. It provides information and draft assistance, not legal advice. It does not file a complaint for you.")

mode = st.toggle("Use local/external AI for fact extraction", value=False,
                 help="Enable after running Ollama locally, or configuring MODEL_BASE_URL / MODEL_NAME. No account required for rules-only mode.")
st.caption("AI mode extracts only evidence-backed facts. The steps and official links always come from a fixed, reviewed source list.")
st.markdown("**Try:** 'I ordered headphones from ShopKart on 12 Oct 2026 for Rs 2,499. Order ID SK12345. They never arrived.'")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "result" not in st.session_state:
    st.session_state.result = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Describe what happened. Do not enter passwords, Aadhaar numbers, or bank details.")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    # Combine the user's corrections/follow-ups; leave out assistant responses.
    narrative = "\n".join(m["content"] for m in st.session_state.messages if m["role"] == "user")
    try:
        st.session_state.result = analyze(narrative, use_model=mode)
        r = st.session_state.result
        response = f"**My understanding:** {r['classification']}"
        if r["followup_question"]:
            response += f"\n\n**One question:** {r['followup_question']}"
        if r["issue_type"] in ("urgent", "out_of_scope", "unknown"):
            response += f"\n\n{r['next_steps'][0]['step']}"
    except ValueError as e:
        response = str(e)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

r = st.session_state.result
if r:
    st.divider()
    st.subheader("Case card")
    st.write(r["classification"])
    st.caption(f"Extraction mode: {r['model_status']}")
    if r["extracted_facts"]:
        st.json(r["extracted_facts"], expanded=True)
    if r["evidence_user_mentioned"]:
        st.write("**Evidence you mentioned:** " + ", ".join(r["evidence_user_mentioned"]))
    if r["evidence_to_collect"]:
        st.write("**Evidence checklist:** " + ", ".join(r["evidence_to_collect"]))
    st.subheader("Suggested next steps")
    for item in r["next_steps"]:
        st.markdown("- " + item["step"])
    if r["source_registry"]:
        with st.expander("Verified official information sources"):
            for src in r["source_registry"]:
                st.markdown(f"- [{src['name']}]({src['url']}) — {src['supports']}")
    st.warning(r["human_escalation"])
    if r["complaint_draft"]:
        st.subheader("Editable complaint draft")
        edited_draft = st.text_area("Review, correct and personalize before sending", value=r["complaint_draft"], height=330, key=f"draft_widget_{len(st.session_state.messages)}")
        st.download_button("Download complaint draft (.txt)", data=edited_draft, file_name="consumer_complaint_draft.txt")
    st.download_button("Download case data (.json)", data=json.dumps(r, indent=2, ensure_ascii=False), file_name="case.json")
if st.button("Start a new case"):
    st.session_state.messages = []
    st.session_state.result = None
    st.rerun()