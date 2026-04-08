# env/data/__init__.py
"""
InboxFlow data package.
Contains synthetic customer profiles, emails, and thread definitions.
"""

from env.data.customers import CUSTOMERS, get_customer, get_customer_by_email
from env.data.emails import EMAILS, get_email, get_emails_for_task, get_emails_by_thread
from env.data.threads import THREADS, get_thread, get_thread_for_email, get_sla_breach_risk_threads

__all__ = [
    "CUSTOMERS", "get_customer", "get_customer_by_email",
    "EMAILS", "get_email", "get_emails_for_task", "get_emails_by_thread",
    "THREADS", "get_thread", "get_thread_for_email", "get_sla_breach_risk_threads",
]