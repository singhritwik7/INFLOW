# env/reward.py
"""
Reward shaping logic.
Wraps graders and applies step-level bonuses and penalties.
Ensures all rewards are in [0.0, 1.0].
"""

from typing import Dict, Any, Tuple
from env.models import InboxAction, InboxReward, RewardBreakdown
from env.graders import (
    grade_inbox_sort,
    grade_inbox_route,
    grade_inbox_crisis,
    _clamp,
)


def compute_reward(
    task_name: str,
    action: InboxAction,
    email_gt: Dict[str, Any],
    thread_gt: Dict[str, Any],
    step: int,
    max_steps: int,
) -> InboxReward:
    """
    Compute shaped reward for a single step.

    Dispatches to correct grader based on task_name.
    Applies step-level shaping on top of grader score.
    Always returns value in [0.0, 1.0].
    """

    # ── Dispatch to correct grader ────────────────────────────────────────
    if task_name == "inbox-sort":
        base_score, breakdown, feedback = grade_inbox_sort(action, email_gt)

    elif task_name == "inbox-route":
        base_score, breakdown, feedback = grade_inbox_route(action, email_gt)

    elif task_name == "inbox-crisis":
        base_score, breakdown, feedback = grade_inbox_crisis(
            action, email_gt, thread_gt
        )
    else:
        raise ValueError(f"Unknown task: {task_name}")

    # ── Step-level shaping ────────────────────────────────────────────────
    shaping_bonus = 0.0
    shaping_penalty = 0.0
    shaping_notes = []

    # Bonus: high score early in episode
    if base_score >= 0.85 and step <= 2:
        shaping_bonus += 0.03
        shaping_notes.append("+quick_correct")

    # Penalty: agent still not done near max_steps
    if not action.done and step >= max_steps - 1:
        shaping_penalty += 0.05
        shaping_notes.append("-near_max_steps")

    # Penalty: escalating everything (spam escalation)
    if action.escalate and email_gt.get("true_category") == "SPAM":
        shaping_penalty += 0.10
        shaping_notes.append("-escalated_spam")

    # Bonus: correct escalation on crisis emails
    if (
        action.escalate
        and email_gt.get("requires_escalation")
        and email_gt.get("true_priority", 0) >= 5
    ):
        shaping_bonus += 0.05
        shaping_notes.append("+crisis_escalation")

    # Bonus: SLA risk flagged correctly on breach-risk thread
    if (
        action.mark_sla_breach_risk
        and thread_gt.get("is_sla_breach_risk")
    ):
        shaping_bonus += 0.03
        shaping_notes.append("+sla_flagged")

    # Apply shaping
    final_score = _clamp(base_score + shaping_bonus - shaping_penalty)

    # Update breakdown totals
    breakdown.bonus = shaping_bonus
    breakdown.penalty = breakdown.penalty + shaping_penalty
    breakdown.total = final_score

    # Build final feedback
    if shaping_notes:
        feedback = feedback + " | shaping: " + ", ".join(shaping_notes)

    return InboxReward(
        value=final_score,
        breakdown=breakdown,
        feedback=feedback,
        is_correct_category=(breakdown.category_score == 1.0),
        is_correct_priority=(breakdown.priority_score == 1.0),
        is_correct_route=(breakdown.routing_score == 1.0),
        is_good_reply=(breakdown.reply_score >= 0.7),
        is_correct_escalation=(breakdown.escalation_score == 1.0),
    )


def compute_episode_bonus(
    task_name: str,
    step_rewards: list,
    all_escalations_correct: bool,
    all_sla_handled: bool,
    inbox_cleared: bool,
) -> float:
    """
    End-of-episode bonus added to final score calculation.
    Returns a bonus value in [0.0, 0.25].
    """
    bonus = 0.0

    if all_escalations_correct:
        bonus += 0.05
    if all_sla_handled and task_name in ["inbox-route", "inbox-crisis"]:
        bonus += 0.10
    if inbox_cleared:
        bonus += 0.05

    # Consistency bonus — all steps above 0.7
    if step_rewards and all(r >= 0.7 for r in step_rewards):
        bonus += 0.05

    return min(bonus, 0.25)