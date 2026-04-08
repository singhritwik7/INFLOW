# InboxFlow — OpenEnv Email Triage Environment

> **Real-world customer support inbox triage for AI agent training and evaluation.**

An AI agent acts as Head of Customer Success for TechCorp, a B2B SaaS company.  
The agent must manage incoming emails with **thread awareness**, **SLA pressure**,  
**customer history**, and **cascading consequences**.

---

## Environment Overview

| Property | Value |
|---|---|
| Domain | Customer Support / Email Triage |
| Tasks | 3 (Easy → Medium → Hard) |
| Reward | Shaped — signal every step |
| Observation | Email + Thread + Customer + SLA context |
| Action Space | Rich — category, priority, routing, reply, escalation |
| API | FastAPI — OpenEnv compliant |

---

## The 3 Tasks

### Task 1: `inbox-sort` (Easy)
Sort a 5-email inbox. Categorize and prioritize each email.  
**Score = category(50%) + priority(50%)**  
Max steps: 8 | Success threshold: 0.70

### Task 2: `inbox-route` (Medium)
Handle an 8-email inbox with threaded conversations.  
Categorize, prioritize, route to correct team, write reply.  
**Score = category(25%) + priority(25%) + routing(30%) + reply(20%)**  
Max steps: 12 | Success threshold: 0.65

### Task 3: `inbox-crisis` (Hard)
Manage a 12-email crisis inbox: SLA breaches, legal threats, angry enterprise customers.  
Full triage: categorize, prioritize, route, reply, escalate, flag SLA risks.  
**Score = category(15%) + priority(15%) + routing(20%) + reply(25%) + escalation(15%) + sla(10%)**  
Max steps: 18 | Success threshold: 0.60

---

## Action Space

```json
{
  "email_id": "email_001",
  "category": "BILLING",
  "priority": 4,
  "done": true,
  "route_to": "billing",
  "reply_draft": "We sincerely apologize for the invoice error...",
  "reply_tone": "apologetic",
  "escalate": false,
  "escalation_reason": null,
  "mark_sla_breach_risk": false
}
```

**Valid categories:** `TECHNICAL | BILLING | INQUIRY | COMPLAINT | SPAM | COMPLIMENT | URGENT`  
**Valid routes:** `engineering | billing | sales | manager | self | close`  
**Valid tones:** `empathetic | formal | apologetic | informative | friendly | warm | enthusiastic | formal_apologetic`

---

## Observation Space

Each step the agent receives:
- **Current email** — subject, body, sender, timestamp, sentiment
- **Thread history** — previous emails in same conversation
- **Thread info** — SLA deadline, breach risk, sentiment trend
- **Customer profile** — plan tier, MRR, sentiment history, SLA tier, notes
- **Inbox summary** — remaining emails, urgent count, SLA risk count
- **Feedback** — reward explanation from last step

---

## Setup & Usage

### Local Development

```bash
# 1. Clone and install
git clone <your-repo>
cd inboxflow
pip install -r requirements.txt

# 2. Start server
python server.py

# 3. Test health
curl http://localhost:7860/health

# 4. Run inference
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_token"
python inference.py
```

### Docker

```bash
docker build -t inboxflow .
docker run -p 7860:7860 \
  -e API_BASE_URL="https://router.huggingface.co/v1" \
  -e MODEL_NAME="Qwen/Qwen2.5-72B-Instruct" \
  -e HF_TOKEN="your_token" \
  inboxflow
```

### API Usage

```python
import httpx

# Reset environment
resp = httpx.post("http://localhost:7860/reset",
                  json={"task_name": "inbox-sort"})
obs = resp.json()["observation"]

# Take step
action = {
    "email_id": obs["current_email"]["id"],
    "category": "BILLING",
    "priority": 4,
    "done": True,
}
resp = httpx.post("http://localhost:7860/step", json=action)
print(resp.json()["reward"])
```

---

## Baseline Scores

| Task | Model | Score | Steps |
|---|---|---|---|
| inbox-sort | Qwen2.5-72B | ~0.75 | 5 |
| inbox-route | Qwen2.5-72B | ~0.62 | 8 |
| inbox-crisis | Qwen2.5-72B | ~0.51 | 10 |

---

## Reward Design

Reward is shaped — never sparse. Every step gives signal.

| Component | Task 1 | Task 2 | Task 3 |
|---|---|---|---|
| Category accuracy | 50% | 25% | 15% |
| Priority accuracy | 50% | 25% | 15% |
| Routing correctness | — | 30% | 20% |
| Reply quality | — | 20% | 25% |
| Escalation | — | — | 15% |
| SLA awareness | — | — | 10% |

**Bonuses:** Fast correct actions, all SLA handled, inbox cleared, consistency  
**Penalties:** Spam escalation, wrong routing, replying to spam, near max steps

---

## Project Structure

```
inboxflow/
├── env/
│   ├── inboxflow_env.py   # Main environment
│   ├── models.py          # Pydantic models
│   ├── tasks.py           # Task definitions
│   ├── graders.py         # Scoring functions
│   ├── reward.py          # Reward shaping
│   └── data/
│       ├── customers.py   # Customer profiles
│       ├── emails.py      # Email dataset
│       └── threads.py     # Thread definitions
├── server.py              # FastAPI server
├── inference.py           # Baseline inference script
├── openenv.yaml           # OpenEnv spec
├── Dockerfile
├── requirements.txt
└── README.md
```