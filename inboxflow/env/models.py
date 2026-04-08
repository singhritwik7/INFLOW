# env/models.py
"""
All Pydantic models for InboxFlow OpenEnv environment.
Observation, Action, Reward, and supporting types.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# ─── Supporting Models ────────────────────────────────────────────────────────

class CustomerProfile(BaseModel):
    id: str
    name: str
    email: str
    company: str
    plan: str                          # Starter | Business | Enterprise | none
    mrr: int
    account_age_days: int
    open_tickets: int
    sentiment_history: List[str]
    last_sentiment: str
    sla_tier: str
    tags: List[str]
    notes: str


class EmailData(BaseModel):
    id: str
    subject: str
    body: str
    sender_email: str
    customer_id: str
    timestamp: str
    thread_id: str
    is_thread_starter: bool
    sentiment: str
    sla_hours: Optional[int] = None


class ThreadInfo(BaseModel):
    id: str
    subject: str
    status: str
    sla_deadline: Optional[str] = None
    is_sla_breach_risk: bool
    thread_sentiment_trend: str
    context_summary: str
    email_count: int


class InboxSummary(BaseModel):
    total_emails: int
    processed: int
    remaining: int
    urgent_count: int
    sla_breach_risk_count: int
    categories_seen: List[str]


class RewardBreakdown(BaseModel):
    category_score: float = 0.0
    priority_score: float = 0.0
    routing_score: float = 0.0
    reply_score: float = 0.0
    tone_score: float = 0.0
    escalation_score: float = 0.0
    sla_score: float = 0.0
    penalty: float = 0.0
    bonus: float = 0.0
    total: float = 0.0


# ─── OBSERVATION — What the agent sees ───────────────────────────────────────

class InboxObservation(BaseModel):
    """
    Full observation returned by reset() and step().
    Contains current email, thread context, customer profile,
    inbox overview, and task instructions.
    """

    # Current email to act on
    current_email: EmailData

    # Thread history (emails before this one in same thread)
    thread_history: List[EmailData] = Field(default_factory=list)

    # Thread metadata
    thread_info: Optional[ThreadInfo] = None

    # Customer context
    customer_profile: CustomerProfile

    # Inbox state
    inbox_summary: InboxSummary

    # Task context
    task_name: str
    step: int
    max_steps: int
    instruction: str

    # SLA context
    sla_deadline: Optional[str] = None
    sla_breach_risk: bool = False
    time_remaining_sla: Optional[str] = None

    # Feedback from last step (empty on first step)
    last_action_feedback: str = ""
    score_so_far: float = 0.0

    # What actions are valid this step
    available_actions: List[str] = Field(default_factory=list)

    # Error from last action (null if none)
    last_action_error: Optional[str] = None


# ─── ACTION — What the agent can do ──────────────────────────────────────────

VALID_CATEGORIES = [
    "TECHNICAL", "BILLING", "INQUIRY",
    "COMPLAINT", "SPAM", "COMPLIMENT", "URGENT"
]

VALID_ROUTES = [
    "engineering", "billing", "sales",
    "manager", "self", "close"
]

VALID_TONES = [
    "empathetic", "formal", "apologetic",
    "informative", "friendly", "warm",
    "enthusiastic", "formal_apologetic"
]


class InboxAction(BaseModel):
    """
    Action taken by agent on a single email.

    Required fields (all tasks):
      - email_id: which email you are acting on
      - category: classification label
      - priority: 1 (low) to 5 (critical)
      - done: True when finished with this email

    Optional fields (task 2+):
      - route_to: which team to route to
      - reply_draft: text of reply to send
      - reply_tone: tone of the reply

    Optional fields (task 3 only):
      - escalate: flag for escalation
      - escalation_reason: why escalating
      - snooze_hours: defer email by N hours
      - merge_with_thread: merge into existing thread
      - mark_sla_breach_risk: flag SLA risk
    """

    # REQUIRED
    email_id: str = Field(..., description="ID of email being acted on")
    category: str = Field(..., description="TECHNICAL|BILLING|INQUIRY|COMPLAINT|SPAM|COMPLIMENT|URGENT")
    priority: int = Field(..., ge=1, le=5, description="Priority 1 (low) to 5 (critical)")
    done: bool = Field(..., description="True when agent is finished with this email")

    # TASK 2+ FIELDS
    route_to: Optional[str] = Field(None, description="engineering|billing|sales|manager|self|close")
    reply_draft: Optional[str] = Field(None, description="Full text of reply to send customer")
    reply_tone: Optional[str] = Field(None, description="Tone of reply")

    # TASK 3 FIELDS
    escalate: Optional[bool] = Field(None, description="Whether to escalate this email")
    escalation_reason: Optional[str] = Field(None, description="Reason for escalation")
    snooze_hours: Optional[int] = Field(None, ge=1, le=72, description="Defer email by N hours")
    merge_with_thread: Optional[str] = Field(None, description="Thread ID to merge with")
    mark_sla_breach_risk: Optional[bool] = Field(None, description="Flag as SLA breach risk")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {VALID_CATEGORIES}"
            )
        return v

    @field_validator("route_to")
    @classmethod
    def validate_route(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ROUTES:
            raise ValueError(
                f"Invalid route '{v}'. Must be one of: {VALID_ROUTES}"
            )
        return v

    @field_validator("reply_tone")
    @classmethod
    def validate_tone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TONES:
            raise ValueError(
                f"Invalid tone '{v}'. Must be one of: {VALID_TONES}"
            )
        return v


# ─── REWARD — Returned by step() ─────────────────────────────────────────────

class InboxReward(BaseModel):
    """
    Reward signal returned after each step.
    Always in [0.0, 1.0].
    Breakdown shows contribution of each component.
    """
    value: float = Field(..., ge=0.0, le=1.0, description="Total reward [0.0, 1.0]")
    breakdown: RewardBreakdown
    feedback: str = Field(..., description="Human-readable explanation of reward")
    is_correct_category: bool = False
    is_correct_priority: bool = False
    is_correct_route: bool = False
    is_good_reply: bool = False
    is_correct_escalation: bool = False


# ─── STEP RESULT — Full return from step() ───────────────────────────────────

class StepResult(BaseModel):
    observation: InboxObservation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


# ─── RESET RESULT — Return from reset() ──────────────────────────────────────

class ResetResult(BaseModel):
    observation: InboxObservation
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)