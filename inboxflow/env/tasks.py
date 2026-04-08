# env/tasks.py
"""
Task definitions for all 3 InboxFlow tasks.
Each task defines its email set, max steps, and grader.
"""

from typing import Dict, Any, List
from env.data.emails import get_emails_for_task

TASK_REGISTRY: Dict[str, Dict[str, Any]] = {

    "inbox-sort": {
        "name": "inbox-sort",
        "display_name": "Inbox Sort",
        "difficulty": "easy",
        "description": (
            "Sort a 5-email inbox by categorizing each email "
            "and assigning a priority level. "
            "No routing or replies needed."
        ),
        "max_steps": 8,
        "email_ids": [
            "email_001",
            "email_002",
            "email_003",
            "email_004",
            "email_005",
        ],
        "grader": "grade_inbox_sort",
        "score_weights": {
            "category": 0.50,
            "priority": 0.50,
        },
        "instruction": (
            "You are a customer support agent. "
            "For each email:\n"
            "1. Set 'category' to one of: "
            "TECHNICAL, BILLING, INQUIRY, COMPLAINT, SPAM, COMPLIMENT, URGENT\n"
            "2. Set 'priority' to 1 (low) through 5 (critical)\n"
            "3. Set 'done' to true when finished with the email\n"
            "Focus only on category and priority — no routing or replies needed."
        ),
        "available_actions": [
            "category", "priority", "done"
        ],
        "success_threshold": 0.70,
    },

    "inbox-route": {
        "name": "inbox-route",
        "display_name": "Inbox Route",
        "difficulty": "medium",
        "description": (
            "Handle an 8-email inbox with some threaded conversations. "
            "Categorize, prioritize, route to the correct team, "
            "and write a one-line reply summary."
        ),
        "max_steps": 12,
        "email_ids": [
            "email_001",
            "email_002",
            "email_003",
            "email_005",
            "email_006",
            "email_007",
            "email_008",
            "email_009",
            "email_010",
        ],
        "grader": "grade_inbox_route",
        "score_weights": {
            "category": 0.25,
            "priority": 0.25,
            "routing": 0.30,
            "reply": 0.20,
        },
        "instruction": (
            "You are a senior customer support agent. "
            "For each email:\n"
            "1. Set 'category': TECHNICAL|BILLING|INQUIRY|COMPLAINT|SPAM|COMPLIMENT|URGENT\n"
            "2. Set 'priority': 1 (low) to 5 (critical)\n"
            "3. Set 'route_to': engineering|billing|sales|manager|self|close\n"
            "4. Set 'reply_draft': a professional reply to the customer (or leave empty for SPAM)\n"
            "5. Set 'done': true when finished\n"
            "Read thread history carefully — context matters for routing decisions."
        ),
        "available_actions": [
            "category", "priority", "route_to", "reply_draft", "done"
        ],
        "success_threshold": 0.65,
    },

    "inbox-crisis": {
        "name": "inbox-crisis",
        "display_name": "Inbox Crisis",
        "difficulty": "hard",
        "description": (
            "Manage a 12-email crisis inbox with SLA breaches, "
            "angry enterprise customers, legal threats, and cascading threads. "
            "Full triage required: categorize, prioritize, route, reply, "
            "escalate appropriately, and flag SLA risks."
        ),
        "max_steps": 18,
        "email_ids": [
            "email_001",
            "email_005",
            "email_006",
            "email_007",
            "email_008",
            "email_011",
            "email_012",
            "email_013",
            "email_014",
            "email_015",
        ],
        "grader": "grade_inbox_crisis",
        "score_weights": {
            "category": 0.15,
            "priority": 0.15,
            "routing": 0.20,
            "reply": 0.25,
            "escalation": 0.15,
            "sla": 0.10,
        },
        "instruction": (
            "You are the Head of Customer Success facing a crisis inbox. "
            "For each email you must:\n"
            "1. category: TECHNICAL|BILLING|INQUIRY|COMPLAINT|SPAM|COMPLIMENT|URGENT\n"
            "2. priority: 1 (low) to 5 (critical) — several are P5\n"
            "3. route_to: engineering|billing|sales|manager|self|close\n"
            "4. reply_draft: write a full professional reply\n"
            "5. reply_tone: empathetic|formal|apologetic|informative|friendly|formal_apologetic\n"
            "6. escalate: true/false — escalate P4+ complaints and legal threats\n"
            "7. escalation_reason: why you are escalating\n"
            "8. mark_sla_breach_risk: true if SLA may be breached\n"
            "9. done: true when finished\n\n"
            "CRITICAL: Read thread history. Multiple emails are follow-ups. "
            "Enterprise customers (MediaGiant, FinanceHub, Mendez) are highest priority. "
            "Legal threats must be escalated to manager immediately."
        ),
        "available_actions": [
            "category", "priority", "route_to", "reply_draft",
            "reply_tone", "escalate", "escalation_reason",
            "mark_sla_breach_risk", "done"
        ],
        "success_threshold": 0.60,
    },
}


def get_task(task_name: str) -> Dict[str, Any]:
    """Get task config by name."""
    if task_name not in TASK_REGISTRY:
        raise ValueError(
            f"Unknown task '{task_name}'. "
            f"Available: {list(TASK_REGISTRY.keys())}"
        )
    return TASK_REGISTRY[task_name]


def list_tasks() -> List[str]:
    """Return all task names."""
    return list(TASK_REGISTRY.keys())