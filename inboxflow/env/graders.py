# env/graders.py
"""
Grading functions for all 3 tasks.
Each grader takes an action and email ground truth,
returns a float score in [0.0, 1.0].

All graders are deterministic and reproducible.
"""

from typing import Dict, Any, Optional
from env.models import InboxAction, RewardBreakdown


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


# ─── CATEGORY GRADER ─────────────────────────────────────────────────────────

def grade_category(
    predicted: str,
    true_category: str,
    sentiment: str = "neutral"
) -> float:
    """
    Score category prediction.

    Rules:
      Exact match              → 1.0
      URGENT predicted, high priority email → 0.5 (partial)
      Wrong but close          → 0.2
      Completely wrong         → 0.0
    """
    if predicted == true_category:
        return 1.0

    # Partial credit matrix — related categories
    partial_credit = {
        ("COMPLAINT", "BILLING"): 0.3,
        ("BILLING", "COMPLAINT"): 0.3,
        ("COMPLAINT", "TECHNICAL"): 0.3,
        ("TECHNICAL", "COMPLAINT"): 0.3,
        ("INQUIRY", "COMPLIMENT"): 0.2,
        ("COMPLIMENT", "INQUIRY"): 0.2,
        ("URGENT", "TECHNICAL"): 0.4,
        ("URGENT", "COMPLAINT"): 0.4,
        ("TECHNICAL", "URGENT"): 0.4,
        ("COMPLAINT", "URGENT"): 0.4,
    }

    pair = (predicted, true_category)
    return partial_credit.get(pair, 0.0)


# ─── PRIORITY GRADER ─────────────────────────────────────────────────────────

def grade_priority(predicted: int, true_priority: int) -> float:
    """
    Score priority prediction.

    Rules:
      Exact match       → 1.0
      Off by 1          → 0.6
      Off by 2          → 0.3
      Off by 3+         → 0.0
    """
    diff = abs(predicted - true_priority)
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.6
    elif diff == 2:
        return 0.3
    else:
        return 0.0


# ─── ROUTING GRADER ──────────────────────────────────────────────────────────

def grade_routing(predicted_route: Optional[str], true_route: str) -> float:
    """
    Score routing decision.

    Rules:
      Exact match       → 1.0
      Close alternative → 0.4
      Wrong             → 0.0
      None provided     → 0.0
    """
    if predicted_route is None:
        return 0.0

    if predicted_route == true_route:
        return 1.0

    # Acceptable alternatives
    partial_routes = {
        ("manager", "engineering"): 0.5,
        ("engineering", "manager"): 0.5,
        ("manager", "billing"): 0.4,
        ("billing", "manager"): 0.4,
        ("self", "billing"): 0.2,
        ("billing", "self"): 0.2,
        ("manager", "sales"): 0.3,
        ("sales", "manager"): 0.3,
    }

    pair = (predicted_route, true_route)
    return partial_routes.get(pair, 0.0)


# ─── REPLY GRADER ────────────────────────────────────────────────────────────

def grade_reply(
    reply_draft: Optional[str],
    ideal_keywords: list,
    requires_reply: bool,
    true_category: str
) -> float:
    """
    Score reply draft quality.

    Rules:
      If no reply required and no reply given → 1.0 (correct)
      If no reply required but reply given → 0.5 (wasted effort)
      If reply required and no reply → 0.0
      If reply given: keyword overlap ratio with bonus for length
    """
    if not requires_reply:
        if reply_draft is None or reply_draft.strip() == "":
            return 1.0
        else:
            # Replied to something that didn't need a reply (SPAM etc)
            if true_category == "SPAM":
                return 0.0
            return 0.5

    # Reply was required
    if reply_draft is None or reply_draft.strip() == "":
        return 0.0

    if not ideal_keywords:
        # No keywords to check — reward non-empty reply
        return 0.7 if len(reply_draft) > 20 else 0.3

    # Keyword matching (case insensitive)
    reply_lower = reply_draft.lower()
    hits = sum(
        1 for kw in ideal_keywords
        if kw.lower() in reply_lower
    )
    keyword_score = hits / len(ideal_keywords)

    # Length bonus — substantive replies rewarded
    length_bonus = 0.0
    if len(reply_draft) > 100:
        length_bonus = 0.1
    if len(reply_draft) > 200:
        length_bonus = 0.15

    return _clamp(keyword_score + length_bonus)


# ─── TONE GRADER ─────────────────────────────────────────────────────────────

def grade_tone(
    predicted_tone: Optional[str],
    ideal_tone: Optional[str],
    customer_sentiment: str
) -> float:
    """
    Score reply tone appropriateness.

    Angry customer needs empathetic/apologetic tone.
    Happy customer can have friendly/warm tone.
    Legal/formal context needs formal tone.
    """
    if predicted_tone is None or ideal_tone is None:
        return 0.5  # neutral — no tone info

    if predicted_tone == ideal_tone:
        return 1.0

    # Sentiment-based partial credit
    tone_compatibility = {
        ("apologetic", "formal_apologetic"): 0.8,
        ("formal_apologetic", "apologetic"): 0.8,
        ("empathetic", "apologetic"): 0.7,
        ("apologetic", "empathetic"): 0.7,
        ("friendly", "warm"): 0.9,
        ("warm", "friendly"): 0.9,
        ("informative", "friendly"): 0.6,
        ("friendly", "informative"): 0.6,
        ("formal", "formal_apologetic"): 0.7,
        ("formal_apologetic", "formal"): 0.7,
        ("enthusiastic", "friendly"): 0.8,
        ("friendly", "enthusiastic"): 0.8,
    }

    pair = (predicted_tone, ideal_tone)
    base_score = tone_compatibility.get(pair, 0.1)

    # Extra penalty: formal tone to angry customer without apology
    if customer_sentiment in ["angry", "furious"]:
        if predicted_tone == "formal":
            return base_score * 0.5

    return base_score


# ─── ESCALATION GRADER ───────────────────────────────────────────────────────

def grade_escalation(
    predicted_escalate: Optional[bool],
    requires_escalation: bool,
    true_priority: int
) -> float:
    """
    Score escalation decision.

    Correct escalation on critical email → 1.0
    Correct non-escalation on normal email → 1.0
    False alarm escalation → 0.2 (overloads managers)
    Missed escalation on critical → 0.0
    """
    if predicted_escalate is None:
        # Not provided — penalize only if escalation was needed
        if requires_escalation:
            return 0.0
        return 0.8  # slight penalty for not being explicit

    if predicted_escalate == requires_escalation:
        return 1.0

    if predicted_escalate and not requires_escalation:
        # False alarm
        return 0.2

    if not predicted_escalate and requires_escalation:
        # Missed escalation — serious failure
        return 0.0

    return 0.5


# ─── SLA GRADER ──────────────────────────────────────────────────────────────

def grade_sla_handling(
    marked_sla_risk: Optional[bool],
    is_sla_breach_risk: bool,
    priority: int,
    true_priority: int
) -> float:
    """
    Score SLA breach risk awareness.
    """
    if not is_sla_breach_risk:
        # No SLA risk — correct to not mark it
        if marked_sla_risk is None or not marked_sla_risk:
            return 1.0
        else:
            return 0.5  # false alarm

    # There IS SLA risk
    if marked_sla_risk is True:
        return 1.0

    # Didn't mark it but got high priority right
    if true_priority >= 4 and priority >= 4:
        return 0.5

    return 0.0


# ─── TASK 1 GRADER — inbox-sort ──────────────────────────────────────────────

def grade_inbox_sort(
    action: InboxAction,
    email_gt: Dict[str, Any]
) -> tuple[float, RewardBreakdown, str]:
    """
    Task 1: inbox-sort grader.
    Score = (category × 0.5) + (priority × 0.5)
    Returns: (score, breakdown, feedback_text)
    """
    cat_score = grade_category(
        action.category,
        email_gt["true_category"],
        email_gt.get("sentiment", "neutral")
    )
    pri_score = grade_priority(action.priority, email_gt["true_priority"])

    total = _clamp((cat_score * 0.5) + (pri_score * 0.5))

    breakdown = RewardBreakdown(
        category_score=cat_score,
        priority_score=pri_score,
        total=total
    )

    feedback_parts = []
    if cat_score == 1.0:
        feedback_parts.append(f"✓ Category correct ({action.category})")
    elif cat_score > 0:
        feedback_parts.append(
            f"~ Category partial ({action.category} vs {email_gt['true_category']})"
        )
    else:
        feedback_parts.append(
            f"✗ Category wrong ({action.category} vs {email_gt['true_category']})"
        )

    if pri_score == 1.0:
        feedback_parts.append(f"✓ Priority correct ({action.priority})")
    elif pri_score > 0:
        feedback_parts.append(
            f"~ Priority close ({action.priority} vs {email_gt['true_priority']})"
        )
    else:
        feedback_parts.append(
            f"✗ Priority wrong ({action.priority} vs {email_gt['true_priority']})"
        )

    return total, breakdown, " | ".join(feedback_parts)


# ─── TASK 2 GRADER — inbox-route ─────────────────────────────────────────────

def grade_inbox_route(
    action: InboxAction,
    email_gt: Dict[str, Any]
) -> tuple[float, RewardBreakdown, str]:
    """
    Task 2: inbox-route grader.
    Score = (category×0.25) + (priority×0.25) + (routing×0.30) + (reply×0.20)
    """
    cat_score = grade_category(
        action.category,
        email_gt["true_category"],
        email_gt.get("sentiment", "neutral")
    )
    pri_score = grade_priority(action.priority, email_gt["true_priority"])
    route_score = grade_routing(action.route_to, email_gt["true_route"])
    reply_score = grade_reply(
        action.reply_draft,
        email_gt.get("ideal_reply_keywords", []),
        email_gt.get("requires_reply", True),
        email_gt["true_category"]
    )

    total = _clamp(
        (cat_score * 0.25)
        + (pri_score * 0.25)
        + (route_score * 0.30)
        + (reply_score * 0.20)
    )

    breakdown = RewardBreakdown(
        category_score=cat_score,
        priority_score=pri_score,
        routing_score=route_score,
        reply_score=reply_score,
        total=total
    )

    feedback_parts = []
    feedback_parts.append(
        f"cat={'✓' if cat_score==1.0 else '~' if cat_score>0 else '✗'}"
        f"({action.category})"
    )
    feedback_parts.append(
        f"pri={'✓' if pri_score==1.0 else '~' if pri_score>0 else '✗'}"
        f"({action.priority})"
    )
    feedback_parts.append(
        f"route={'✓' if route_score==1.0 else '~' if route_score>0 else '✗'}"
        f"({action.route_to})"
    )
    feedback_parts.append(
        f"reply={'✓' if reply_score>=0.7 else '~' if reply_score>0 else '✗'}"
        f"({reply_score:.2f})"
    )

    return total, breakdown, " | ".join(feedback_parts)


# ─── TASK 3 GRADER — inbox-crisis ────────────────────────────────────────────

def grade_inbox_crisis(
    action: InboxAction,
    email_gt: Dict[str, Any],
    thread_gt: Dict[str, Any]
) -> tuple[float, RewardBreakdown, str]:
    """
    Task 3: inbox-crisis grader.
    Score = category×0.15 + priority×0.15 + routing×0.20
          + reply×0.25 + escalation×0.15 + sla×0.10
    """
    cat_score = grade_category(
        action.category,
        email_gt["true_category"],
        email_gt.get("sentiment", "neutral")
    )
    pri_score = grade_priority(action.priority, email_gt["true_priority"])
    route_score = grade_routing(action.route_to, email_gt["true_route"])
    reply_score = grade_reply(
        action.reply_draft,
        email_gt.get("ideal_reply_keywords", []),
        email_gt.get("requires_reply", True),
        email_gt["true_category"]
    )
    tone_score = grade_tone(
        action.reply_tone,
        email_gt.get("reply_tone"),
        email_gt.get("sentiment", "neutral")
    )
    escalation_score = grade_escalation(
        action.escalate,
        email_gt.get("requires_escalation", False),
        email_gt["true_priority"]
    )
    sla_score = grade_sla_handling(
        action.mark_sla_breach_risk,
        thread_gt.get("is_sla_breach_risk", False),
        action.priority,
        email_gt["true_priority"]
    )

    # Penalty for replying to SPAM
    penalty = 0.0
    if email_gt["true_category"] == "SPAM" and action.reply_draft:
        penalty = 0.15

    # Combined reply quality includes tone
    combined_reply = _clamp((reply_score * 0.7) + (tone_score * 0.3))

    total = _clamp(
        (cat_score * 0.15)
        + (pri_score * 0.15)
        + (route_score * 0.20)
        + (combined_reply * 0.25)
        + (escalation_score * 0.15)
        + (sla_score * 0.10)
        - penalty
    )

    breakdown = RewardBreakdown(
        category_score=cat_score,
        priority_score=pri_score,
        routing_score=route_score,
        reply_score=reply_score,
        tone_score=tone_score,
        escalation_score=escalation_score,
        sla_score=sla_score,
        penalty=penalty,
        total=total
    )

    feedback_parts = [
        f"cat={'✓' if cat_score==1.0 else '~' if cat_score>0 else '✗'}",
        f"pri={'✓' if pri_score==1.0 else '~' if pri_score>0 else '✗'}",
        f"route={'✓' if route_score==1.0 else '~' if route_score>0 else '✗'}",
        f"reply={reply_score:.2f}",
        f"tone={tone_score:.2f}",
        f"escalate={'✓' if escalation_score==1.0 else '✗'}",
        f"sla={'✓' if sla_score==1.0 else '~' if sla_score>0 else '✗'}",
        f"penalty={penalty:.2f}",
        f"TOTAL={total:.2f}",
    ]

    return total, breakdown, " | ".join(feedback_parts)