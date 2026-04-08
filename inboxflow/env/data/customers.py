# env/data/customers.py
"""
Customer profiles for InboxFlow environment.
10 customers across different plan tiers with history.
"""

from typing import Dict, Any

CUSTOMERS: Dict[str, Dict[str, Any]] = {

    "cust_001": {
        "id": "cust_001",
        "name": "Sarah Chen",
        "email": "sarah.chen@techcorp-client.com",
        "company": "FinanceHub Inc",
        "plan": "Enterprise",
        "mrr": 5000,
        "account_age_days": 847,
        "open_tickets": 2,
        "total_tickets_lifetime": 14,
        "sentiment_history": ["neutral", "neutral", "angry", "angry"],
        "last_sentiment": "angry",
        "sla_tier": "4hour",
        "csm_assigned": "alice@techcorp.com",
        "tags": ["at-risk", "high-value"],
        "notes": "Has threatened to churn twice this quarter"
    },

    "cust_002": {
        "id": "cust_002",
        "name": "James Okafor",
        "email": "james.okafor@startup.io",
        "company": "LaunchPad Startup",
        "plan": "Starter",
        "mrr": 49,
        "account_age_days": 32,
        "open_tickets": 0,
        "total_tickets_lifetime": 2,
        "sentiment_history": ["happy", "neutral"],
        "last_sentiment": "neutral",
        "sla_tier": "48hour",
        "csm_assigned": None,
        "tags": ["new-customer"],
        "notes": "Recently onboarded"
    },

    "cust_003": {
        "id": "cust_003",
        "name": "Maria Rodriguez",
        "email": "m.rodriguez@globalretail.com",
        "company": "Global Retail Corp",
        "plan": "Business",
        "mrr": 1200,
        "account_age_days": 423,
        "open_tickets": 1,
        "total_tickets_lifetime": 8,
        "sentiment_history": ["neutral", "happy", "neutral"],
        "last_sentiment": "neutral",
        "sla_tier": "8hour",
        "csm_assigned": "bob@techcorp.com",
        "tags": ["stable"],
        "notes": "Reliable payer, occasional billing questions"
    },

    "cust_004": {
        "id": "cust_004",
        "name": "Derek Walsh",
        "email": "derek.walsh@mediagiant.tv",
        "company": "MediaGiant Television",
        "plan": "Enterprise",
        "mrr": 12000,
        "account_age_days": 1205,
        "open_tickets": 3,
        "total_tickets_lifetime": 31,
        "sentiment_history": ["angry", "angry", "angry", "furious"],
        "last_sentiment": "furious",
        "sla_tier": "2hour",
        "csm_assigned": "alice@techcorp.com",
        "tags": ["at-risk", "high-value", "escalation-pending", "pr-risk"],
        "notes": "VP level. Has contact with our CEO. Legal threat made."
    },

    "cust_005": {
        "id": "cust_005",
        "name": "Priya Nair",
        "email": "priya.nair@healthtech.ai",
        "company": "HealthTech AI",
        "plan": "Business",
        "mrr": 800,
        "account_age_days": 156,
        "open_tickets": 0,
        "total_tickets_lifetime": 3,
        "sentiment_history": ["happy", "happy", "happy"],
        "last_sentiment": "happy",
        "sla_tier": "8hour",
        "csm_assigned": "bob@techcorp.com",
        "tags": ["champion", "expansion-candidate"],
        "notes": "Loves the product. Potential upsell to Enterprise."
    },

    "cust_006": {
        "id": "cust_006",
        "name": "Unknown Sender",
        "email": "noreply@spamblast99.com",
        "company": "Unknown",
        "plan": "none",
        "mrr": 0,
        "account_age_days": 0,
        "open_tickets": 0,
        "total_tickets_lifetime": 0,
        "sentiment_history": [],
        "last_sentiment": "neutral",
        "sla_tier": "none",
        "csm_assigned": None,
        "tags": ["spam-suspected"],
        "notes": "Not a real customer"
    },

    "cust_007": {
        "id": "cust_007",
        "name": "Tom Brennan",
        "email": "tom.brennan@legalfirm.law",
        "company": "Brennan & Associates Legal",
        "plan": "Business",
        "mrr": 600,
        "account_age_days": 89,
        "open_tickets": 1,
        "total_tickets_lifetime": 4,
        "sentiment_history": ["neutral", "frustrated"],
        "last_sentiment": "frustrated",
        "sla_tier": "8hour",
        "csm_assigned": None,
        "tags": ["compliance-sensitive"],
        "notes": "Legal firm — very sensitive about data privacy"
    },

    "cust_008": {
        "id": "cust_008",
        "name": "Angela Kim",
        "email": "angela.kim@ecomstore.shop",
        "company": "EcomStore",
        "plan": "Starter",
        "mrr": 49,
        "account_age_days": 14,
        "open_tickets": 0,
        "total_tickets_lifetime": 1,
        "sentiment_history": ["happy"],
        "last_sentiment": "happy",
        "sla_tier": "48hour",
        "csm_assigned": None,
        "tags": ["new-customer"],
        "notes": "Brand new user — onboarding phase"
    },

    "cust_009": {
        "id": "cust_009",
        "name": "Carlos Mendez",
        "email": "c.mendez@manufacturing.mx",
        "company": "Mendez Manufacturing",
        "plan": "Enterprise",
        "mrr": 7500,
        "account_age_days": 634,
        "open_tickets": 2,
        "total_tickets_lifetime": 19,
        "sentiment_history": ["neutral", "frustrated", "neutral", "frustrated"],
        "last_sentiment": "frustrated",
        "sla_tier": "4hour",
        "csm_assigned": "alice@techcorp.com",
        "tags": ["high-value", "recurring-issues"],
        "notes": "Recurring API integration problems"
    },

    "cust_010": {
        "id": "cust_010",
        "name": "Sophie Laurent",
        "email": "s.laurent@designstudio.fr",
        "company": "Laurent Design Studio",
        "plan": "Business",
        "mrr": 299,
        "account_age_days": 201,
        "open_tickets": 0,
        "total_tickets_lifetime": 2,
        "sentiment_history": ["happy", "neutral"],
        "last_sentiment": "neutral",
        "sla_tier": "8hour",
        "csm_assigned": None,
        "tags": [],
        "notes": "Quiet customer, pays reliably"
    },
}


def get_customer(customer_id: str) -> Dict[str, Any]:
    """Get customer profile by ID."""
    return CUSTOMERS.get(customer_id, CUSTOMERS["cust_006"])


def get_customer_by_email(email: str) -> Dict[str, Any]:
    """Find customer by email address."""
    for cust in CUSTOMERS.values():
        if cust["email"] == email:
            return cust
    return CUSTOMERS["cust_006"]