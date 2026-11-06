"""Curated procedural pointers, not an exhaustive legal database.
Verified from official Indian government sources on 2026-11-06.
No model may add a statute, case citation, entitlement, or deadline.
"""

SOURCES = [
    {
        "id": "NCH_ABOUT",
        "name": "National Consumer Helpline: About",
        "url": "https://consumerhelpline.gov.in/public/about",
        "supports": "Pre-litigation consumer grievance registration; unresolved grievances may be taken to a Consumer Commission.",
    },
    {
        "id": "NCH_CONTACT",
        "name": "National Consumer Helpline: Contact",
        "url": "https://consumerhelpline.gov.in/public/contact",
        "supports": "Official portal and helpline 1915, WhatsApp 8800001915.",
    },
    {
        "id": "EJAGRITI",
        "name": "e-Jagriti: Consumer Commissions",
        "url": "https://e-jagriti.gov.in/",
        "supports": "Official consumer commission portal with registration and complaint workflow.",
    },
    {
        "id": "CONSUMER_ACT",
        "name": "India Code: Consumer Protection Act, 2019",
        "url": "https://www.indiacode.nic.in/indiacode/handle/123456789/15256?sam_handle=123456789%2F1362&view_type=browse",
        "supports": "Official text/index of the Consumer Protection Act, 2019; do not infer a particular section applies.",
    },
]

NEXT_STEPS = [
    {
        "step": "Contact the seller/platform grievance or customer-support channel and request a written resolution.",
        "source_ids": [],
        "kind": "practical",
    },
    {
        "step": "If unresolved, consider registering a pre-litigation consumer grievance with the National Consumer Helpline (1915 or consumerhelpline.gov.in).",
        "source_ids": ["NCH_ABOUT", "NCH_CONTACT"],
        "kind": "official_process",
    },
    {
        "step": "If still unresolved, check whether filing with the appropriate Consumer Commission through e-Jagriti is suitable; get individual legal advice before formal filing.",
        "source_ids": ["NCH_ABOUT", "EJAGRITI"],
        "kind": "official_process",
    },
]
