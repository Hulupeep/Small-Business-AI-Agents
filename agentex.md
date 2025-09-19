Create 10 agents like these in langchain. Each should be self explainable

They’re written in **Python** with the current LangChain style (tools + ChatOpenAI).  
---

Here are some examples

# 1) Lead-Qualifier → CRM (Supabase/Airtable)

**What it does:** Reads inbound text (email/form/WhatsApp), qualifies (budget, need, timeline), and writes a lead row.

```python
# pip install langchain langchain-openai langchain-community python-dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import os

# --- Tool: upsert_lead --------------------------------------------------------
class Lead(BaseModel):
    name: str = Field(..., description="Lead full name if known, else 'Unknown'")
    channel: str = Field(..., description="email|form|whatsapp|phone")
    need: str = Field(..., description="What they want")
    budget_eur: int = Field(..., description="Budget in euro, 0 if unknown")
    timeline: str = Field(..., description="Timeline words, e.g. '2 weeks'")

def upsert_lead_tool(lead: Lead) -> str:
    # TODO: replace with Supabase/Airtable insert
    # e.g., supabase.table("leads").upsert(lead.dict())
    print("UPSERT:", lead.dict())
    return "Lead stored."

upsert_lead = StructuredTool.from_function(
    func=upsert_lead_tool,
    name="upsert_lead",
    description="Store or update a qualified lead in the CRM",
    args_schema=Lead,
)

# --- Agent --------------------------------------------------------------------
SYSTEM = """You qualify small-business inbound messages. Be concrete. 
If budget unknown, infer a range conservatively. Always store the lead."""
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Inbound text:\n{inbound_text}\nChannel: {channel}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, tools=[upsert_lead], prompt=PROMPT)
executor = AgentExecutor(agent=agent, tools=[upsert_lead], verbose=True)

# Example run
resp = executor.invoke({
    "inbound_text": "Hi, we need a 3-page site, simple booking, under €2k, start next month.",
    "channel": "email",
})
print(resp["output"])
```

**Why this wedge:** measurable value in <1 day—every SMB needs consistent lead capture + qualification.

---

# 2) Appointment Scheduler → Cal.com/Google Calendar

**What it does:** Converts natural language into a booking. If slot unknown, proposes top 3 options and drafts a reply.

```python
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

class Booking(BaseModel):
    name: str
    service: str = Field(..., description="e.g., 'consultation', 'cut & color', 'repair'")
    duration_min: int
    earliest_start_iso: str = Field(..., description="Client earliest acceptable start, ISO8601")
    phone_or_email: str

def create_booking_tool(b: Booking) -> str:
    # TODO: call Cal.com or Google Calendar API; here we mock a slot.
    start = datetime.fromisoformat(b.earliest_start_iso)
    slot = start.replace(minute=0, second=0, microsecond=0)
    return f"Booked {b.service} for {b.name} at {slot.isoformat()} for {b.duration_min} min."

create_booking = StructuredTool.from_function(
    func=create_booking_tool, name="create_booking",
    description="Create a calendar booking for a client", args_schema=Booking
)

SYSTEM = """You are a scheduling agent for a small business. 
If details are missing (duration, earliest time, contact), infer sensibly and proceed."""
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Client message: {msg}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [create_booking], PROMPT)
executor = AgentExecutor(agent=agent, tools=[create_booking], verbose=True)

resp = executor.invoke({"msg": "Can you fit me for a 45 min consultation sometime after 2pm today? I'm Anna, 085-111-2222"})
print(resp["output"])
```

**Why this wedge:** converts demand → revenue instantly. Great for hair, clinics, trades, consultants.

---

# 3) Invoice Chaser + Draft Email

**What it does:** Finds overdue invoice cues in text/CSV, drafts a polite email with firm tone ladder.

```python
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

class ChaseEmailReq(BaseModel):
    client_name: str
    invoice_number: str
    amount_eur: float
    days_overdue: int
    recipient_email: str

def draft_chase_email(req: ChaseEmailReq) -> str:
    tone = "friendly reminder" if req.days_overdue < 14 else "firm reminder"
    return f"""Subject: Invoice {req.invoice_number} – {tone}

Hi {req.client_name},

Just a quick note that invoice {req.invoice_number} ({req.amount_eur:.2f} EUR) is now {req.days_overdue} days overdue.
Could you confirm payment date? If already paid, thank you—please ignore.

Best,
Accounts
"""
draft_email = StructuredTool.from_function(
    func=draft_chase_email, name="draft_chase_email",
    description="Drafts a polite but effective invoice chase email.", args_schema=ChaseEmailReq
)

SYSTEM = "You help SMBs recover cash. Always produce a professional email via the tool."
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Overdue details: {details}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [draft_email], PROMPT)
exec = AgentExecutor(agent=agent, tools=[draft_email], verbose=True)

resp = exec.invoke({"details": "{'client_name':'ACME','invoice_number':'INV-102','amount_eur':980,'days_overdue':21,'recipient_email':'ap@acme.com'}"})
print(resp["output"])
```

**Why this wedge:** direct path to **cash in**—often pays for itself in week 1.

---

# 4) FAQ / RAG over Your Docs (policies, services, pricing)

**What it does:** Answers customer queries from your own docs using embeddings.

```python
# pip install chromadb langchain-text-splitters
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import ChatPromptTemplate

docs = [
    ("services.md", "We offer emergency callouts 24/7 within Galway City. Standard rate €120 callout + €60/hr."),
    ("pricing.md", "Website packages: Starter €1,500; Pro €3,500; Custom per quote. Hosting €25/mo."),
]
splits = []
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
for name, text in docs:
    for c in splitter.split_text(text):
        splits.append({"source": name, "text": c})

emb = OpenAIEmbeddings(model="text-embedding-3-small")
vs = Chroma.from_documents(
    documents=[(s["text"]) for s in splits],
    embedding=emb,
    metadatas=[{"source": s["source"]} for s in splits],
    collection_name="biz"
)

def search_docs(q: str) -> str:
    hits = vs.similarity_search(q, k=3)
    out = []
    for h in hits:
        out.append(f"- {h.page_content} (src: {h.metadata.get('source')})")
    return "\n".join(out) or "No matches."

search_tool = Tool.from_function(
    func=search_docs,
    name="search_docs",
    description="Semantic search over business docs: services, pricing, policies."
)

SYSTEM = "Answer strictly from search results. Cite source. If unknown, say so."
PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "Question: {q}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [search_tool], PROMPT)
executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)

print(executor.invoke({"q":"Do you cover weekend emergencies in Galway and how much would it cost to start?"})["output"])
```

**Why this wedge:** reduces owner time on repetitive queries; consistent answers; upsell hooks.

---

# 5) Social Post Generator (Offer-First)

**What it does:** Turns today’s availability or promo into on-brand posts (FB/IG/Google Business).

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
prompt = ChatPromptTemplate.from_template("""
Brand: {brand}. Niche: {niche}. Offer: {offer}.
Generate 3 short posts (platform-neutral) with a crisp CTA and phone/booking link placeholder.
Keep it local to {area}. Avoid hashtags spam; max 2 per post.
""")
print(llm.invoke(prompt.format_messages(
    brand="Clarinbridge Repairs", niche="appliance repair",
    offer="Same-day dishwasher diagnostics €49", area="South Galway"
)).content)
```

**Why this wedge:** quick demand gen; pair with a CTA to your booking agent.

---

## How to Ship This Fast

1. **Create a new repo** with a `requirements.txt` (langchain, langchain-openai, langchain-community, chromadb, python-dotenv).
2. Add **one agent** (lead-qualifier or scheduler) and wire a real API (Supabase/Cal.com).
3. Expose a **FastAPI endpoint** `/webhook` for inbound messages; forward WhatsApp/Twilio/email into it.
4. Measure: **#qualified leads, #bookings, € recovered**. Put those on a tiny admin dashboard.
5. Charge: **€99–€299/mo** per business for “Done-4-You AI Reception + Collections.” Upsell RAG FAQ as Pro.

If you tell me which one you want to make real first (lead capture, booking, collections, or RAG), I’ll drop in the exact **FastAPI route**, **Supabase table schema**, and a **.env template** so you can deploy today.

