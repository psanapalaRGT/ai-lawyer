"""Build the required <=2-page PDF from verified prototype facts."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth
from pathlib import Path

ROOT=Path(__file__).parent
OUTPUT=ROOT/'SOLUTION_DOC.pdf'
PAGE_W, PAGE_H=A4
navy=colors.HexColor('#16324A'); teal=colors.HexColor('#007D7A'); muted=colors.HexColor('#4A5A65'); pale=colors.HexColor('#EDF5F4')
styles={
 'micro':ParagraphStyle('micro',fontName='Helvetica-Bold',fontSize=7.7,leading=10,textColor=teal,spaceAfter=5),
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=18,leading=21,textColor=navy,spaceAfter=5),
 'sub':ParagraphStyle('sub',fontName='Helvetica',fontSize=9,leading=12,textColor=muted,spaceAfter=10),
 'h':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=10,leading=13,textColor=navy,spaceBefore=9,spaceAfter=4),
 'p':ParagraphStyle('p',fontName='Helvetica',fontSize=8.8,leading=12.2,textColor=navy,spaceAfter=6),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.65,leading=10.25,textColor=navy,spaceAfter=3),
 'tiny':ParagraphStyle('tiny',fontName='Helvetica',fontSize=7.2,leading=9.1,textColor=navy),
 'headcell':ParagraphStyle('headcell',fontName='Helvetica-Bold',fontSize=7.5,leading=9.5,textColor=colors.white),
 'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=7.35,leading=9.4,textColor=navy),
}

def P(text,kind='p'):
    return Paragraph(text,styles[kind])

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#D7E0E2'))
    canvas.line(40,38,PAGE_W-40,38)
    canvas.setFont('Helvetica',7)
    canvas.setFillColor(muted)
    canvas.drawString(40,27,'Kuku AI Generalist Assignment | Problem 2 | Candidate draft - review before submission')
    canvas.drawRightString(PAGE_W-40,27,f'Page {doc.page} of 2')
    canvas.restoreState()

story=[]
story += [P('PROBLEM 2  /  AI LAWYER  /  WORKING MICRO-PILOT','micro'),
          P('NyayaSaathi | Evidence-first refund help','title'),
          P('A narrowly scoped conversational assistant for Indian consumers with online purchase, non-delivery or refund disputes.','sub'),
          P('Problem choice and assumptions','h'),
          P('Many consumers can describe what went wrong but not organize it into a complaint. I chose a single checkable workflow instead of claiming an AI lawyer can handle all Indian law. Assumptions: text input, Indian consumer shopping context, no real-time legal filing, and the user reviews the resulting draft. Landlord, salary, criminal and urgent safety matters are explicitly outside this pilot.'),
          P('One real input-to-output demonstration','h')]
example = [
    [P('<b>Input</b>','small'),P('"I ordered headphones from ShopKart on 12 Oct 2026 for Rs 2,499. Order ID SK12345. It never arrived. I emailed twice."','small')],
    [P('<b>Output</b>','small'),P('Issue: non-delivery; seller: ShopKart; amount: 2,499; order: SK12345. Evidence: seller emails. Next: seller grievance channel, National Consumer Helpline, and potentially consumer commission. An editable complaint letter is generated.','small')],
]
t=Table(example,colWidths=[65,450]); t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),pale),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEBELOW',(0,0),(-1,0),.5,colors.white)
])); story.append(t)
story += [P('How it works: what AI does vs. code','h')]
work = [
    [P('01  Capture','headcell'),P('02  Extract','headcell'),P('03  Check','headcell'),P('04  Assist','headcell')],
    [P('User describes a messy situation; follow-ups accumulate in a case narrative.','cell'),
     P('Optional, swappable local/API model proposes case fields with exact supporting quotes.','cell'),
     P('Code validates quotes, routes risks, retains unknown fields as placeholders and prohibits new law citations.','cell'),
     P('User sees a case card, evidence checklist, official links and editable letter; nothing is filed automatically.','cell')]
]
t=Table(work,colWidths=[128.75]*4);t.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),teal),('BACKGROUND',(0,1),(-1,1),pale),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('LINEBEFORE',(1,0),(-1,-1),1,colors.white)
]));story.append(t)
story += [P('Build and replay','h'),
          P('<b>Working offline:</b> <font name="Courier">python demo.py "I bought shoes online but they never arrived"</font><br/><b>Repeat tests:</b> <font name="Courier">python run_cases.py</font><br/><b>Chat interface:</b> <font name="Courier">pip install -r requirements.txt</font> then <font name="Courier">streamlit run app.py</font><br/><b>Optional AI:</b> local Ollama <font name="Courier">llama3.2:3b</font>, or any OpenAI-compatible chat endpoint using environment variables. The tested baseline is rules-only; the model path is implemented but was not executed here.','small'),
          P('Safety choices','h'),
          P('LLM output is restricted to evidence-backed fact extraction. All process guidance comes from a curated registry of official Government of India sources; the model cannot fabricate legal sections, precedents, deadlines or a promised outcome. Formal filings and urgent cases are referred to a human. No case history is intentionally persisted by the app.','small'),
          PageBreak()]

story += [P('MEASUREMENT  /  LIMITS  /  SCALE','micro'),
          P('What works - and where it fails','title'),
          P('Reproducible run: 8 synthetic stories; all full output JSON is in <b>raw_outputs/</b>. Offline rules-only classification matched the expected category for <b>7 of 8</b> cases. Unit regression checks also pass. These figures do not demonstrate LLM quality.','p'),
          P('Observed raw-run checks','h')]
rows=[
    ['Case','Tested behavior','Offline classification','Check'],
    ['T01','Paid order not delivered','non_delivery','Match'],
    ['T02','Returned item; no refund','refund_pending','Match*'],
    ['T03','Landlord deposit','out_of_scope','Match'],
    ['T04','Unpaid salary','out_of_scope','Match'],
    ['T05','Asked to invent a law / order ID','non_delivery','Match'],
    ['T06','Threat of physical harm','urgent','Match'],
    ['T07','Hindi non-delivery narrative','non_delivery','Match*'],
    ['T08','"The package is missing"','unknown','Miss'],
]
rows=[[P(str(c),'headcell' if i==0 else 'cell') for c in row] for i,row in enumerate(rows)]
t=Table(rows,colWidths=[48,220,142,105],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,-1),(-1,-1),.7,colors.HexColor('#CAD7DC'))]))
story.append(t)
story += [P('<b>*Beyond category accuracy:</b> T02 misses the seller even though "BuyNow" appears, and T07 gives an English fallback rather than a complete Hindi experience. T08 misses the paraphrase "package is missing." Those are genuine shortcomings in the rule-only path.','small'),
          P('One AI-assisted mistake and how I found it','h'),
          P('The first ChatGPT-assisted regex design misclassified T02 as "unknown" because "returned" was absent from its shopping vocabulary. Running <font name="Courier">run_cases.py</font> exposed the error; I corrected the rule and reran all tests. I retain T08 as a known failure instead of hiding it. The optional live LLM extraction mode still needs measured evaluation.','small'),
          P('Grounded guidance, not invented law','h'),
          P('The National Consumer Helpline explains its pre-litigation grievance route and helpline <b>1915</b>; unresolved matters may proceed to a Consumer Commission. The government e-Jagriti portal provides consumer-commission filing workflows. The Consumer Protection Act, 2019 is listed as an official reference but no specific provision is asserted for a user without review.','small'),
          P('<b>Verified references:</b> consumerhelpline.gov.in/public/about  |  consumerhelpline.gov.in/public/contact<br/>e-jagriti.gov.in  |  indiacode.nic.in (Consumer Protection Act, 2019)','small'),
          P('How to scale and what it costs','h'),
          P('The workflow is stateless per narrative and suitable for batch processing. Add a narrowly validated new category with a curated source set and its own failure tests; version the registry and require human review of high-risk cases. Baseline needs no paid API; local model costs depend on hardware. A cloud model is optional and incurs provider-dependent usage charges. The same adapter can swap models without changing the safety and drafting layer.','small'),
          P('Tools and hand-off','h'),
          P('<b>Used for this draft:</b> ChatGPT (scope, code, prompts and document drafting), Python (real test execution), official Indian government sites (procedural grounding). <b>Not yet tested:</b> Ollama model responses. Candidate should review every claim, personalize the decisions and demo a fresh input during the interview.','small')]

SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=42,bottomMargin=51,title='NyayaSaathi - Kuku AI Generalist Assignment (Problem 2)',author='Assignment prototype (candidate review required)').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUTPUT)
