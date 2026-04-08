# env/data/emails.py
"""
30 synthetic emails with full ground truth labels.
Used across all 3 tasks.
"""

from typing import Dict, Any, List

EMAILS: Dict[str, Dict[str, Any]] = {

    # ─── TASK 1 EMAILS (inbox-sort) — 5 isolated, clear-cut ───────────────

    "email_001": {
        "id": "email_001",
        "subject": "Invoice #INV-2024-0892 is incorrect",
        "body": (
            "Hi Support Team,\n\n"
            "I just received Invoice #INV-2024-0892 and the amount is wrong. "
            "We were charged $5,000 but our contract says $4,200 per month. "
            "Please correct this immediately and send a revised invoice.\n\n"
            "Thanks,\nSarah Chen\nFinanceHub Inc"
        ),
        "sender_email": "sarah.chen@techcorp-client.com",
        "customer_id": "cust_001",
        "timestamp": "2024-01-15T09:23:00",
        "thread_id": "thread_001",
        "is_thread_starter": True,
        # GROUND TRUTH
        "true_category": "BILLING",
        "true_priority": 4,
        "true_route": "billing",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "frustrated",
        "sla_hours": 4,
        "ideal_reply_keywords": [
            "apologize", "invoice", "corrected", "revised",
            "billing team", "review", "resolve"
        ],
        "reply_tone": "apologetic",
        "task_ids": ["inbox-sort", "inbox-route", "inbox-crisis"],
    },

    "email_002": {
        "id": "email_002",
        "subject": "How do I export data to CSV?",
        "body": (
            "Hello,\n\n"
            "Quick question — I'm trying to export my dashboard data to CSV "
            "but I can't find the option anywhere. Is this a feature you support?\n\n"
            "Best,\nJames Okafor"
        ),
        "sender_email": "james.okafor@startup.io",
        "customer_id": "cust_002",
        "timestamp": "2024-01-15T09:45:00",
        "thread_id": "thread_002",
        "is_thread_starter": True,
        "true_category": "INQUIRY",
        "true_priority": 2,
        "true_route": "self",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "neutral",
        "sla_hours": 48,
        "ideal_reply_keywords": [
            "export", "CSV", "dashboard", "settings",
            "download", "feature", "guide"
        ],
        "reply_tone": "informative",
        "task_ids": ["inbox-sort", "inbox-route"],
    },

    "email_003": {
        "id": "email_003",
        "subject": "MAKE MONEY FAST — Business Opportunity!!!",
        "body": (
            "Dear Business Owner,\n\n"
            "Congratulations! You have been selected for an EXCLUSIVE "
            "business opportunity. Click here to claim your $10,000 reward. "
            "Limited time offer. Act NOW!\n\n"
            "- The Team at GlobalWealth"
        ),
        "sender_email": "noreply@spamblast99.com",
        "customer_id": "cust_006",
        "timestamp": "2024-01-15T10:00:00",
        "thread_id": "thread_003",
        "is_thread_starter": True,
        "true_category": "SPAM",
        "true_priority": 1,
        "true_route": "close",
        "requires_escalation": False,
        "requires_reply": False,
        "sentiment": "neutral",
        "sla_hours": None,
        "ideal_reply_keywords": [],
        "reply_tone": None,
        "task_ids": ["inbox-sort", "inbox-route"],
    },

    "email_004": {
        "id": "email_004",
        "subject": "Your platform is incredible — thank you!",
        "body": (
            "Hi team,\n\n"
            "Just wanted to say — your platform has completely transformed "
            "how we manage our health data workflows. The API integration "
            "was seamless and the support from Bob has been outstanding.\n\n"
            "We are planning to expand our usage next quarter!\n\n"
            "Warm regards,\nPriya Nair\nHealthTech AI"
        ),
        "sender_email": "priya.nair@healthtech.ai",
        "customer_id": "cust_005",
        "timestamp": "2024-01-15T10:15:00",
        "thread_id": "thread_004",
        "is_thread_starter": True,
        "true_category": "COMPLIMENT",
        "true_priority": 2,
        "true_route": "self",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "happy",
        "sla_hours": 8,
        "ideal_reply_keywords": [
            "thank", "appreciate", "glad", "excited",
            "expansion", "support", "team"
        ],
        "reply_tone": "warm",
        "task_ids": ["inbox-sort"],
    },

    "email_005": {
        "id": "email_005",
        "subject": "API returning 500 errors — production is DOWN",
        "body": (
            "URGENT — Our entire production system is down.\n\n"
            "Your API has been returning 500 errors for the past 30 minutes. "
            "We have 50,000 active users affected. "
            "This is a P0 incident for us.\n\n"
            "I need someone on the phone NOW.\n\n"
            "Carlos Mendez\nCTO, Mendez Manufacturing\n"
            "Phone: +52-555-0192"
        ),
        "sender_email": "c.mendez@manufacturing.mx",
        "customer_id": "cust_009",
        "timestamp": "2024-01-15T10:30:00",
        "thread_id": "thread_005",
        "is_thread_starter": True,
        "true_category": "TECHNICAL",
        "true_priority": 5,
        "true_route": "engineering",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "angry",
        "sla_hours": 4,
        "ideal_reply_keywords": [
            "urgent", "escalated", "engineering team", "investigating",
            "P0", "priority", "call", "30 minutes", "update"
        ],
        "reply_tone": "apologetic",
        "task_ids": ["inbox-sort", "inbox-route", "inbox-crisis"],
    },

    # ─── TASK 2 EMAILS (inbox-route) — 8 emails, some threaded ────────────

    "email_006": {
        "id": "email_006",
        "subject": "Re: API returning 500 errors — production is DOWN",
        "body": (
            "It has now been 45 minutes. STILL DOWN.\n\n"
            "I have escalated internally to our CEO. "
            "If this is not resolved in 15 minutes we are switching providers.\n\n"
            "Carlos Mendez"
        ),
        "sender_email": "c.mendez@manufacturing.mx",
        "customer_id": "cust_009",
        "timestamp": "2024-01-15T11:15:00",
        "thread_id": "thread_005",
        "is_thread_starter": False,
        "true_category": "TECHNICAL",
        "true_priority": 5,
        "true_route": "manager",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "furious",
        "sla_hours": 4,
        "ideal_reply_keywords": [
            "sincerely apologize", "CEO", "manager", "escalated",
            "resolution", "15 minutes", "personally", "fix"
        ],
        "reply_tone": "apologetic",
        "task_ids": ["inbox-route", "inbox-crisis"],
    },

    "email_007": {
        "id": "email_007",
        "subject": "Data privacy question — GDPR compliance",
        "body": (
            "Dear Support,\n\n"
            "We need clarification on your GDPR data processing agreement. "
            "Specifically: where is EU customer data stored? "
            "Do you have a DPA we can sign? "
            "Our legal team requires this before our contract renewal next week.\n\n"
            "Tom Brennan\nBrennan & Associates Legal"
        ),
        "sender_email": "tom.brennan@legalfirm.law",
        "customer_id": "cust_007",
        "timestamp": "2024-01-15T11:30:00",
        "thread_id": "thread_006",
        "is_thread_starter": True,
        "true_category": "COMPLAINT",
        "true_priority": 4,
        "true_route": "manager",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "frustrated",
        "sla_hours": 8,
        "ideal_reply_keywords": [
            "GDPR", "DPA", "data processing", "EU", "compliance",
            "legal", "contract", "renewal", "team"
        ],
        "reply_tone": "formal",
        "task_ids": ["inbox-route", "inbox-crisis"],
    },

    "email_008": {
        "id": "email_008",
        "subject": "Can I get a refund for last month?",
        "body": (
            "Hi,\n\n"
            "I noticed I was charged for last month but I cancelled "
            "my subscription on the 28th of last month. "
            "Can I get a pro-rated refund for the days after cancellation?\n\n"
            "Thanks,\nMaria Rodriguez\nGlobal Retail Corp"
        ),
        "sender_email": "m.rodriguez@globalretail.com",
        "customer_id": "cust_003",
        "timestamp": "2024-01-15T12:00:00",
        "thread_id": "thread_007",
        "is_thread_starter": True,
        "true_category": "BILLING",
        "true_priority": 3,
        "true_route": "billing",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "neutral",
        "sla_hours": 8,
        "ideal_reply_keywords": [
            "refund", "pro-rated", "billing", "cancellation",
            "process", "review", "account"
        ],
        "reply_tone": "empathetic",
        "task_ids": ["inbox-route", "inbox-crisis"],
    },

    "email_009": {
        "id": "email_009",
        "subject": "Getting started — how do I invite my team?",
        "body": (
            "Hello!\n\n"
            "Just signed up and loving it so far. "
            "How do I invite my teammates to join my workspace?\n\n"
            "Angela Kim\nEcomStore"
        ),
        "sender_email": "angela.kim@ecomstore.shop",
        "customer_id": "cust_008",
        "timestamp": "2024-01-15T12:30:00",
        "thread_id": "thread_008",
        "is_thread_starter": True,
        "true_category": "INQUIRY",
        "true_priority": 2,
        "true_route": "self",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "happy",
        "sla_hours": 48,
        "ideal_reply_keywords": [
            "invite", "team", "workspace", "settings",
            "members", "email", "link"
        ],
        "reply_tone": "friendly",
        "task_ids": ["inbox-route"],
    },

    "email_010": {
        "id": "email_010",
        "subject": "Feature request: Dark mode",
        "body": (
            "Hi team,\n\n"
            "Would love to see dark mode added to the dashboard. "
            "Many of my team members work late and the bright screen "
            "is hard on the eyes. Any plans for this?\n\n"
            "Sophie Laurent\nLaurent Design Studio"
        ),
        "sender_email": "s.laurent@designstudio.fr",
        "customer_id": "cust_010",
        "timestamp": "2024-01-15T13:00:00",
        "thread_id": "thread_009",
        "is_thread_starter": True,
        "true_category": "INQUIRY",
        "true_priority": 1,
        "true_route": "self",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "neutral",
        "sla_hours": 8,
        "ideal_reply_keywords": [
            "dark mode", "feature request", "roadmap",
            "noted", "team", "future"
        ],
        "reply_tone": "friendly",
        "task_ids": ["inbox-route"],
    },

    # ─── TASK 3 EMAILS (inbox-crisis) — 12 emails, high stakes ───────────

    "email_011": {
        "id": "email_011",
        "subject": "FORMAL COMPLAINT — Service failure + legal action notice",
        "body": (
            "To Whom It May Concern,\n\n"
            "I am writing to formally notify you that MediaGiant Television "
            "is considering legal action regarding your persistent service failures.\n\n"
            "Over the past 3 months we have experienced:\n"
            "- 14 hours of unplanned downtime\n"
            "- 3 missed SLA commitments\n"
            "- Zero proactive communication\n\n"
            "Our legal team has been instructed. "
            "I expect a call from your CEO within 24 hours.\n\n"
            "Derek Walsh\nVP Operations, MediaGiant Television\n"
            "Direct: +1-555-0284"
        ),
        "sender_email": "derek.walsh@mediagiant.tv",
        "customer_id": "cust_004",
        "timestamp": "2024-01-15T08:00:00",
        "thread_id": "thread_010",
        "is_thread_starter": True,
        "true_category": "COMPLAINT",
        "true_priority": 5,
        "true_route": "manager",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "furious",
        "sla_hours": 2,
        "ideal_reply_keywords": [
            "formal", "CEO", "legal", "acknowledge",
            "24 hours", "escalated", "compensate", "urgent review"
        ],
        "reply_tone": "formal_apologetic",
        "task_ids": ["inbox-crisis"],
    },

    "email_012": {
        "id": "email_012",
        "subject": "Re: Invoice #INV-2024-0892 is incorrect — STILL NOT FIXED",
        "body": (
            "It has been 3 days since my first email about the wrong invoice.\n\n"
            "Nothing has been done. I have now been charged the wrong amount "
            "AGAIN this month. This is now a pattern.\n\n"
            "I will be disputing these charges with our bank if not resolved TODAY.\n\n"
            "Sarah Chen\nFinanceHub Inc"
        ),
        "sender_email": "sarah.chen@techcorp-client.com",
        "customer_id": "cust_001",
        "timestamp": "2024-01-15T08:30:00",
        "thread_id": "thread_001",
        "is_thread_starter": False,
        "true_category": "BILLING",
        "true_priority": 5,
        "true_route": "billing",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "furious",
        "sla_hours": 4,
        "ideal_reply_keywords": [
            "resolve today", "billing manager", "personally",
            "credit", "apologize", "priority", "call"
        ],
        "reply_tone": "apologetic",
        "task_ids": ["inbox-crisis"],
    },

    "email_013": {
        "id": "email_013",
        "subject": "Re: GDPR compliance — still waiting",
        "body": (
            "Following up on my earlier email about GDPR.\n\n"
            "Our contract renewal is TOMORROW and we still have no DPA.\n"
            "If we cannot confirm GDPR compliance by end of day, "
            "we will not be renewing our contract.\n\n"
            "Tom Brennan"
        ),
        "sender_email": "tom.brennan@legalfirm.law",
        "customer_id": "cust_007",
        "timestamp": "2024-01-15T09:00:00",
        "thread_id": "thread_006",
        "is_thread_starter": False,
        "true_category": "COMPLAINT",
        "true_priority": 5,
        "true_route": "manager",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "furious",
        "sla_hours": 2,
        "ideal_reply_keywords": [
            "DPA", "today", "legal team", "GDPR",
            "renewal", "compliance", "urgent", "sent"
        ],
        "reply_tone": "formal",
        "task_ids": ["inbox-crisis"],
    },

    "email_014": {
        "id": "email_014",
        "subject": "Interested in upgrading to Enterprise plan",
        "body": (
            "Hi team,\n\n"
            "We have grown a lot and think Enterprise plan is right for us now. "
            "Can someone from sales reach out to discuss pricing and features?\n\n"
            "Priya Nair\nHealthTech AI"
        ),
        "sender_email": "priya.nair@healthtech.ai",
        "customer_id": "cust_005",
        "timestamp": "2024-01-15T09:15:00",
        "thread_id": "thread_011",
        "is_thread_starter": True,
        "true_category": "INQUIRY",
        "true_priority": 3,
        "true_route": "sales",
        "requires_escalation": False,
        "requires_reply": True,
        "sentiment": "happy",
        "sla_hours": 8,
        "ideal_reply_keywords": [
            "sales", "Enterprise", "reach out", "pricing",
            "upgrade", "team", "today"
        ],
        "reply_tone": "enthusiastic",
        "task_ids": ["inbox-crisis"],
    },

    "email_015": {
        "id": "email_015",
        "subject": "Re: API 500 errors — we are switching providers",
        "body": (
            "You have had 2 hours to fix this.\n\n"
            "We are now migrating to a competitor. "
            "Please send our data export immediately — "
            "we are exercising our right to data portability.\n\n"
            "Carlos Mendez\nCTO, Mendez Manufacturing"
        ),
        "sender_email": "c.mendez@manufacturing.mx",
        "customer_id": "cust_009",
        "timestamp": "2024-01-15T12:30:00",
        "thread_id": "thread_005",
        "is_thread_starter": False,
        "true_category": "COMPLAINT",
        "true_priority": 5,
        "true_route": "manager",
        "requires_escalation": True,
        "requires_reply": True,
        "sentiment": "furious",
        "sla_hours": 2,
        "ideal_reply_keywords": [
            "retain", "data export", "CEO", "compensation",
            "resolve", "immediately", "personal", "escalated"
        ],
        "reply_tone": "formal_apologetic",
        "task_ids": ["inbox-crisis"],
    },
}


def get_email(email_id: str) -> Dict[str, Any]:
    """Get email by ID."""
    return EMAILS.get(email_id, {})


def get_emails_for_task(task_name: str) -> List[Dict[str, Any]]:
    """Get all emails belonging to a specific task."""
    return [
        email for email in EMAILS.values()
        if task_name in email.get("task_ids", [])
    ]


def get_emails_by_thread(thread_id: str) -> List[Dict[str, Any]]:
    """Get all emails in a thread, sorted by timestamp."""
    thread_emails = [
        email for email in EMAILS.values()
        if email.get("thread_id") == thread_id
    ]
    return sorted(thread_emails, key=lambda e: e["timestamp"])