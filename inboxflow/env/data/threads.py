# env/data/threads.py
"""
Thread definitions linking emails together.
Includes SLA deadlines and thread metadata.
"""

from typing import Dict, Any

THREADS: Dict[str, Dict[str, Any]] = {

    "thread_001": {
        "id": "thread_001",
        "subject": "Invoice #INV-2024-0892 is incorrect",
        "customer_id": "cust_001",
        "email_ids": ["email_001", "email_012"],
        "status": "open",
        "sla_deadline": "2024-01-15T13:23:00",
        "sla_hours": 4,
        "is_sla_breach_risk": True,
        "thread_sentiment_trend": "escalating",
        "context_summary": (
            "Customer reported incorrect invoice 3 days ago. "
            "No resolution provided. Customer now threatening bank dispute. "
            "Second incorrect charge issued."
        ),
    },

    "thread_002": {
        "id": "thread_002",
        "subject": "How do I export data to CSV?",
        "customer_id": "cust_002",
        "email_ids": ["email_002"],
        "status": "open",
        "sla_deadline": "2024-01-17T09:45:00",
        "sla_hours": 48,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "stable",
        "context_summary": "New customer asking basic how-to question.",
    },

    "thread_003": {
        "id": "thread_003",
        "subject": "MAKE MONEY FAST",
        "customer_id": "cust_006",
        "email_ids": ["email_003"],
        "status": "open",
        "sla_deadline": None,
        "sla_hours": None,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "neutral",
        "context_summary": "Suspected spam. No real customer.",
    },

    "thread_004": {
        "id": "thread_004",
        "subject": "Platform feedback",
        "customer_id": "cust_005",
        "email_ids": ["email_004"],
        "status": "open",
        "sla_deadline": "2024-01-15T18:15:00",
        "sla_hours": 8,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "positive",
        "context_summary": "Happy customer giving positive feedback. Expansion candidate.",
    },

    "thread_005": {
        "id": "thread_005",
        "subject": "API 500 errors — production down",
        "customer_id": "cust_009",
        "email_ids": ["email_005", "email_006", "email_015"],
        "status": "open",
        "sla_deadline": "2024-01-15T14:30:00",
        "sla_hours": 4,
        "is_sla_breach_risk": True,
        "thread_sentiment_trend": "escalating",
        "context_summary": (
            "P0 production outage. Customer escalating to CEO level. "
            "Now threatening to switch providers and requesting data export. "
            "Engineering must be involved immediately."
        ),
    },

    "thread_006": {
        "id": "thread_006",
        "subject": "GDPR compliance inquiry",
        "customer_id": "cust_007",
        "email_ids": ["email_007", "email_013"],
        "status": "open",
        "sla_deadline": "2024-01-15T19:30:00",
        "sla_hours": 8,
        "is_sla_breach_risk": True,
        "thread_sentiment_trend": "escalating",
        "context_summary": (
            "Legal firm needs GDPR DPA before contract renewal tomorrow. "
            "No response has been sent. Customer now threatening not to renew."
        ),
    },

    "thread_007": {
        "id": "thread_007",
        "subject": "Refund request",
        "customer_id": "cust_003",
        "email_ids": ["email_008"],
        "status": "open",
        "sla_deadline": "2024-01-15T20:00:00",
        "sla_hours": 8,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "stable",
        "context_summary": "Standard refund request for cancelled subscription.",
    },

    "thread_008": {
        "id": "thread_008",
        "subject": "Onboarding question",
        "customer_id": "cust_008",
        "email_ids": ["email_009"],
        "status": "open",
        "sla_deadline": "2024-01-17T12:30:00",
        "sla_hours": 48,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "positive",
        "context_summary": "New happy customer asking onboarding question.",
    },

    "thread_009": {
        "id": "thread_009",
        "subject": "Dark mode feature request",
        "customer_id": "cust_010",
        "email_ids": ["email_010"],
        "status": "open",
        "sla_deadline": "2024-01-15T21:00:00",
        "sla_hours": 8,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "stable",
        "context_summary": "Feature request from design studio.",
    },

    "thread_010": {
        "id": "thread_010",
        "subject": "Formal complaint + legal notice — MediaGiant",
        "customer_id": "cust_004",
        "email_ids": ["email_011"],
        "status": "open",
        "sla_deadline": "2024-01-15T10:00:00",
        "sla_hours": 2,
        "is_sla_breach_risk": True,
        "thread_sentiment_trend": "critical",
        "context_summary": (
            "VP-level formal complaint with legal action threat. "
            "CEO call demanded within 24 hours. "
            "History of 14 hours downtime. PR risk flagged."
        ),
    },

    "thread_011": {
        "id": "thread_011",
        "subject": "Enterprise upgrade inquiry",
        "customer_id": "cust_005",
        "email_ids": ["email_014"],
        "status": "open",
        "sla_deadline": "2024-01-15T17:15:00",
        "sla_hours": 8,
        "is_sla_breach_risk": False,
        "thread_sentiment_trend": "positive",
        "context_summary": "Happy customer wanting to upgrade. High-value opportunity.",
    },
}


def get_thread(thread_id: str) -> Dict[str, Any]:
    """Get thread by ID."""
    return THREADS.get(thread_id, {})


def get_thread_for_email(email_id: str) -> Dict[str, Any]:
    """Find which thread an email belongs to."""
    for thread in THREADS.values():
        if email_id in thread.get("email_ids", []):
            return thread
    return {}


def get_sla_breach_risk_threads() -> list:
    """Return all threads with SLA breach risk."""
    return [t for t in THREADS.values() if t.get("is_sla_breach_risk")]