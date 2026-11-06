"""Conservative, source-anchored consumer grievance workflow.

An optional LLM extracts data with exact-span provenance. All procedural
recommendations are selected from reviewed copy in knowledge.py.
"""
from __future__ import annotations

import os
import re
from typing import Any

from knowledge import NEXT_STEPS, SOURCES

OUT_OF_SCOPE = re.compile(r"\b(landlord|rent|tenant|security deposit|salary|boss|employer|wages|divorce|custody|property dispute|tax return)\b", re.I)
URGENT = re.compile(r"\b(threaten(?:ed|ing|s)?|assault|violence|arrested|blackmail|physical harm)\b|धमकी|బెదిరింపు", re.I)
NON_DELIVERY = re.compile(r"\b(never arrived|not delivered|didn't arrive|did not arrive|non.delivery|no delivery|missing delivery)\b|ऑर्डर नहीं आया|डिलीवरी नहीं|డెలివరీ కాలేదు|ఆర్డర్ రాలేదు", re.I)
REFUND = re.compile(r"\b(refund|returned|money back|reimbursement|cancelled|canceled)\b|रिफंड|पैसे वापस|వాపసు|రీఫండ్", re.I)
DEFECT = re.compile(r"\b(defective|broken|damaged|faulty|not working|wrong item)\b|खराब|పాడైంది", re.I)
SHOPPING = re.compile(r"\b(order|ordered|bought|purchase|returned|return|seller|platform|online|shop|product|delivery)\b|ऑर्डर|ऑनलाइन|खरीदा|ఆర్డర్|ఆన్‌లైన్", re.I)
AMOUNT = re.compile(r"(?:₹\s*|(?:Rs\.?|INR)\s*\.?\s*)([\d,]+(?:\.\d{1,2})?)", re.I)
ORDER_ID = re.compile(r"\b(?:order\s*(?:id|number|no\.?|#))\s*[:#-]?\s*((?=[A-Za-z0-9-]*\d)[A-Za-z0-9][A-Za-z0-9-]{2,})\b", re.I)
SELLER = re.compile(r"\b(?:from|at|via)\s+([A-Z][A-Za-z0-9&._-]{2,30})\b")
ORDER_DATE = re.compile(r"\b(?:ordered|bought|purchased)\b.{0,45}?\b(?:on\s+)(\d{1,2}\s+[A-Za-z]{3,9}\s+20\d\d|\d{1,2}[/-]\d{1,2}[/-]20\d\d)", re.I)
REFUND_DATE = re.compile(r"\b(?:refund|refunded)\b.{0,45}?\b(?:on|by)\s+(\d{1,2}\s+[A-Za-z]{3,9}\s+20\d\d|\d{1,2}[/-]\d{1,2}[/-]20\d\d)", re.I)
PRODUCT = re.compile(r"\b(?:ordered|bought|purchased|returned)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z -]{2,35}?)(?=\s+(?:from|on|for|but|and|it|that|to|because|online)\b|[.,!?]|$)", re.I)
EVIDENCE = {
    "order confirmation/invoice": r"\b(invoice|order confirmation)\b",
    "payment proof": r"\b(payment receipt|bank statement|transaction (?:id|receipt)|payment proof)\b",
    "seller messages": r"\b(email|emailed|chat|message|whatsapp)\b",
    "return/shipping receipt": r"\b(return receipt|courier receipt|tracking)\b",
    "screenshot(s)": r"\b(screenshot|screen shot)\b",
}


def _baseline(text: str) -> dict[str, Any]:
    facts = {}
    for name, pattern in [("amount", AMOUNT), ("order_id", ORDER_ID), ("seller", SELLER),
                          ("order_date", ORDER_DATE), ("refund_date", REFUND_DATE), ("product", PRODUCT)]:
        m = pattern.search(text)
        if m:
            facts[name] = m.group(1).strip(" .,")
    if URGENT.search(text):
        kind = "urgent"
    elif OUT_OF_SCOPE.search(text):
        kind = "out_of_scope"
    elif NON_DELIVERY.search(text):
        kind = "non_delivery"
    elif DEFECT.search(text) and SHOPPING.search(text):
        kind = "defective_item"
    elif REFUND.search(text) and SHOPPING.search(text):
        kind = "refund_pending"
    else:
        kind = "unknown"
    return {"issue_type": kind, "facts": facts}


def _safe(s: str) -> str:
    # Avoid Markdown/template pollution. Keep user-supplied data as literal text.
    return re.sub(r"[\r\n\t]+", " ", str(s)).replace("<", "").replace(">", "")[:130].strip()


def _draft(facts: dict[str, str], kind: str) -> str:
    seller = _safe(facts.get("seller", "[Seller or platform]"))
    amount = _safe(facts.get("amount", "[amount]"))
    oid = _safe(facts.get("order_id", "[order ID]"))
    product = _safe(facts.get("product", "[product name]"))
    order_date = _safe(facts.get("order_date", "[purchase date]"))
    topic = {"non_delivery": "Non-delivery of order", "refund_pending": "Pending refund",
             "defective_item": "Defective or incorrect product"}.get(kind, "Order concern")
    if kind == "non_delivery":
        detail = "The order has not been delivered."
    elif kind == "refund_pending":
        detail = "I have requested a refund, but I have not received a satisfactory resolution."
    elif kind == "defective_item":
        detail = "I received an item that appears defective or incorrect."
    else:
        detail = "I have an unresolved concern with this purchase."
    return (f"Subject: Complaint - {topic} (Order {oid})\n\n"
            f"To: {seller} Customer Support / Grievance Team\n\n"
            f"I am writing about my purchase of {product} on {order_date}, order number {oid}, "
            f"for Rs {amount}. {detail}\n\n"
            "Please review my order, explain what has happened, and provide an appropriate "
            "resolution, including a refund where applicable. Please acknowledge this complaint "
            "and respond in writing. I can provide relevant invoices, payment records and correspondence.\n\n"
            "Sincerely,\n[Your name]\n[Your preferred contact details]")


def analyze(text: str, use_model: bool = False) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("Enter a description of your issue.")
    if len(text) > 10000:
        raise ValueError("Please keep your description under 10,000 characters.")

    baseline = _baseline(text)
    facts, kind = dict(baseline["facts"]), baseline["issue_type"]
    model_status = "rules_only"
    rejected_fields = []
    if use_model:
        try:
            from model_adapter import extract
            model = extract(text)
            # Never allow a model to downgrade safety escalation.
            if kind not in ("urgent", "out_of_scope"):
                if model["issue_type"] in ("urgent", "out_of_scope"):
                    kind = model["issue_type"]
                elif kind == "unknown":
                    kind = model["issue_type"]
            for k, v in model["facts"].items():
                if k not in facts:
                    facts[k] = v
            rejected_fields = model["rejected_fields"]
            model_status = f"model_extraction:{model['model']}"
        except Exception as exc:
            # No secrets/raw exceptions returned to the UI.
            model_status = f"rules_fallback:{type(exc).__name__}"

    important_missing = [name for name in ("seller", "amount", "order_id") if not facts.get(name)]
    label = {
        "non_delivery": "Online order not delivered",
        "refund_pending": "Refund not received / pending",
        "defective_item": "Defective or incorrect purchase",
        "unknown": "Not enough information to classify safely",
        "out_of_scope": "Outside the online shopping/refund scope",
        "urgent": "Potentially urgent or safety-sensitive issue",
    }[kind]
    found_evidence = [name for name, pat in EVIDENCE.items() if re.search(pat, text, re.I)]
    evidence_to_collect = ["purchase/order receipt", "proof of payment", "seller communication", "delivery/return tracking"]

    if kind in ("non_delivery", "refund_pending", "defective_item"):
        steps = NEXT_STEPS
        draft = _draft(facts, kind)
        needs_lawyer = "If there is a formal legal notice, large loss, disputed facts, or court filing, seek an independent qualified lawyer."
    elif kind == "urgent":
        steps = [{"step": "Seek immediate help from local emergency services if you are unsafe; consult a qualified lawyer or the appropriate authorities.", "source_ids": [], "kind": "safety"}]
        draft = None
        needs_lawyer = "This assistant cannot safely handle threats, violence or urgent legal emergencies."
    elif kind == "out_of_scope":
        steps = [{"step": "This pilot covers only online shopping purchase/refund complaints. For this topic, consult a qualified local lawyer or an appropriate official grievance channel.", "source_ids": [], "kind": "scope"}]
        draft = None
        needs_lawyer = "A specialist should assess laws and facts relevant to your issue."
    else:
        steps = [{"step": "Please describe what was purchased online, what went wrong, and what the seller has done so far.", "source_ids": [], "kind": "clarify"}]
        draft = None
        needs_lawyer = "This assistant has not identified a supported consumer issue."

    followup = (
        "Could you share " + ", ".join({"seller": "the seller/platform name", "amount": "the amount paid", "order_id": "the order ID"}[k] for k in important_missing) + "?"
        if kind in ("non_delivery", "refund_pending", "defective_item") and important_missing else None
    )
    return {
        "issue_type": kind,
        "classification": label,
        "model_status": model_status,
        "extracted_facts": facts,
        "missing_facts": important_missing if kind in ("non_delivery", "refund_pending", "defective_item") else [],
        "evidence_user_mentioned": found_evidence,
        "evidence_to_collect": evidence_to_collect if kind in ("non_delivery", "refund_pending", "defective_item") else [],
        "next_steps": steps,
        "followup_question": followup,
        "complaint_draft": draft,
        "human_escalation": needs_lawyer,
        "source_registry": SOURCES if kind in ("non_delivery", "refund_pending", "defective_item") else [],
        "validation": {"rejected_model_facts": rejected_fields, "never_supplies_statute_numbers": True},
        "disclaimer": "Information and draft assistance, not a lawyer or personalized legal advice. No filings are submitted.",
    }
