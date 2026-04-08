# tests/test_graders.py
"""
Tests for all grader functions.
Verifies scores are always in [0.0, 1.0]
and graders are deterministic and reproducible.
"""

import pytest
from env.graders import (
    grade_category,
    grade_priority,
    grade_routing,
    grade_reply,
    grade_tone,
    grade_escalation,
    grade_sla_handling,
    grade_inbox_sort,
    grade_inbox_route,
    grade_inbox_crisis,
    _clamp,
)
from env.models import InboxAction


# ─── Helper ───────────────────────────────────────────────────────────────────

def make_action(**kwargs) -> InboxAction:
    """Create a test action with defaults."""
    defaults = {
        "email_id": "email_001",
        "category": "BILLING",
        "priority": 4,
        "done": True,
    }
    defaults.update(kwargs)
    return InboxAction(**defaults)


EMAIL_GT_BILLING = {
    "id": "email_001",
    "true_category": "BILLING",
    "true_priority": 4,
    "true_route": "billing",
    "requires_escalation": False,
    "requires_reply": True,
    "sentiment": "frustrated",
    "sla_hours": 4,
    "ideal_reply_keywords": [
        "apologize", "invoice", "corrected",
        "billing team", "resolve"
    ],
    "reply_tone": "apologetic",
}

EMAIL_GT_TECHNICAL = {
    "id": "email_005",
    "true_category": "TECHNICAL",
    "true_priority": 5,
    "true_route": "engineering",
    "requires_escalation": True,
    "requires_reply": True,
    "sentiment": "angry",
    "sla_hours": 4,
    "ideal_reply_keywords": [
        "urgent", "escalated", "engineering team",
        "investigating", "priority"
    ],
    "reply_tone": "apologetic",
}

EMAIL_GT_SPAM = {
    "id": "email_003",
    "true_category": "SPAM",
    "true_priority": 1,
    "true_route": "close",
    "requires_escalation": False,
    "requires_reply": False,
    "sentiment": "neutral",
    "sla_hours": None,
    "ideal_reply_keywords": [],
    "reply_tone": None,
}

THREAD_GT_SLA = {
    "id": "thread_005",
    "is_sla_breach_risk": True,
    "sla_deadline": "2024-01-15T14:30:00",
}

THREAD_GT_NO_SLA = {
    "id": "thread_002",
    "is_sla_breach_risk": False,
    "sla_deadline": None,
}


# ─── Clamp Tests ──────────────────────────────────────────────────────────────

class TestClamp:

    def test_clamp_normal(self):
        assert _clamp(0.5) == 0.5

    def test_clamp_above_one(self):
        assert _clamp(1.5) == 1.0

    def test_clamp_below_zero(self):
        assert _clamp(-0.5) == 0.0

    def test_clamp_exactly_zero(self):
        assert _clamp(0.0) == 0.0

    def test_clamp_exactly_one(self):
        assert _clamp(1.0) == 1.0


# ─── Category Grader Tests ────────────────────────────────────────────────────

class TestGradeCategory:

    def test_exact_match_returns_one(self):
        score = grade_category("BILLING", "BILLING")
        assert score == 1.0

    def test_wrong_category_returns_zero(self):
        score = grade_category("SPAM", "BILLING")
        assert score == 0.0

    def test_partial_credit_complaint_billing(self):
        score = grade_category("COMPLAINT", "BILLING")
        assert 0.0 < score < 1.0

    def test_partial_credit_urgent_technical(self):
        score = grade_category("URGENT", "TECHNICAL")
        assert 0.0 < score < 1.0

    def test_all_categories_exact_match(self):
        categories = [
            "TECHNICAL", "BILLING", "INQUIRY",
            "COMPLAINT", "SPAM", "COMPLIMENT", "URGENT"
        ]
        for cat in categories:
            assert grade_category(cat, cat) == 1.0

    def test_score_always_in_range(self):
        categories = [
            "TECHNICAL", "BILLING", "INQUIRY",
            "COMPLAINT", "SPAM", "COMPLIMENT", "URGENT"
        ]
        for pred in categories:
            for true in categories:
                score = grade_category(pred, true)
                assert 0.0 <= score <= 1.0, (
                    f"Score out of range for ({pred}, {true}): {score}"
                )

    def test_deterministic(self):
        """Same inputs always return same output."""
        score1 = grade_category("BILLING", "TECHNICAL")
        score2 = grade_category("BILLING", "TECHNICAL")
        assert score1 == score2


# ─── Priority Grader Tests ────────────────────────────────────────────────────

class TestGradePriority:

    def test_exact_match(self):
        assert grade_priority(4, 4) == 1.0

    def test_off_by_one(self):
        score = grade_priority(3, 4)
        assert score == 0.6

    def test_off_by_two(self):
        score = grade_priority(2, 4)
        assert score == 0.3

    def test_off_by_three(self):
        score = grade_priority(1, 4)
        assert score == 0.0

    def test_off_by_four(self):
        score = grade_priority(1, 5)
        assert score == 0.0

    def test_all_combinations_in_range(self):
        for pred in range(1, 6):
            for true in range(1, 6):
                score = grade_priority(pred, true)
                assert 0.0 <= score <= 1.0

    def test_symmetric(self):
        """Off by 1 in either direction same score."""
        assert grade_priority(3, 4) == grade_priority(5, 4)

    def test_deterministic(self):
        score1 = grade_priority(3, 5)
        score2 = grade_priority(3, 5)
        assert score1 == score2


# ─── Routing Grader Tests ─────────────────────────────────────────────────────

class TestGradeRouting:

    def test_exact_match(self):
        assert grade_routing("billing", "billing") == 1.0

    def test_none_returns_zero(self):
        assert grade_routing(None, "billing") == 0.0

    def test_wrong_route(self):
        assert grade_routing("sales", "billing") == 0.0

    def test_partial_credit_manager_engineering(self):
        score = grade_routing("manager", "engineering")
        assert 0.0 < score < 1.0

    def test_all_exact_matches(self):
        routes = ["engineering", "billing", "sales", "manager", "self", "close"]
        for route in routes:
            assert grade_routing(route, route) == 1.0

    def test_score_always_in_range(self):
        routes = ["engineering", "billing", "sales", "manager", "self", "close"]
        for pred in routes:
            for true in routes:
                score = grade_routing(pred, true)
                assert 0.0 <= score <= 1.0

    def test_deterministic(self):
        score1 = grade_routing("manager", "billing")
        score2 = grade_routing("manager", "billing")
        assert score1 == score2


# ─── Reply Grader Tests ───────────────────────────────────────────────────────

class TestGradeReply:

    def test_no_reply_required_no_reply_given(self):
        """Correct to not reply to spam."""
        score = grade_reply(None, [], False, "SPAM")
        assert score == 1.0

    def test_spam_with_reply_penalized(self):
        """Replying to spam is penalized."""
        score = grade_reply("Here is my reply", [], False, "SPAM")
        assert score == 0.0

    def test_reply_required_no_reply_given(self):
        """Must reply but did not."""
        score = grade_reply(None, ["apologize", "resolve"], True, "BILLING")
        assert score == 0.0

    def test_reply_with_all_keywords(self):
        """Reply contains all keywords."""
        reply = "We apologize and will resolve the invoice issue with billing team"
        keywords = ["apologize", "resolve", "invoice", "billing team"]
        score = grade_reply(reply, keywords, True, "BILLING")
        assert score > 0.7

    def test_reply_with_no_keywords(self):
        """Reply has no matching keywords."""
        reply = "Thank you for contacting us"
        keywords = ["apologize", "resolve", "invoice"]
        score = grade_reply(reply, keywords, True, "BILLING")
        assert score < 0.5

    def test_long_reply_gets_bonus(self):
        """Longer substantive replies get bonus."""
        short_reply = "Sorry"
        long_reply = (
            "We sincerely apologize for the inconvenience caused by this issue. "
            "Our billing team has been notified and will resolve this immediately. "
            "You will receive a corrected invoice within 24 hours."
        )
        keywords = ["apologize", "billing", "resolve"]
        short_score = grade_reply(short_reply, keywords, True, "BILLING")
        long_score = grade_reply(long_reply, keywords, True, "BILLING")
        assert long_score >= short_score

    def test_score_always_in_range(self):
        test_cases = [
            (None, [], False, "SPAM"),
            (None, ["key"], True, "BILLING"),
            ("reply text", ["key"], True, "BILLING"),
            ("reply text", [], True, "TECHNICAL"),
        ]
        for reply, keywords, required, category in test_cases:
            score = grade_reply(reply, keywords, required, category)
            assert 0.0 <= score <= 1.0

    def test_deterministic(self):
        reply = "We apologize for the invoice error"
        keywords = ["apologize", "invoice"]
        score1 = grade_reply(reply, keywords, True, "BILLING")
        score2 = grade_reply(reply, keywords, True, "BILLING")
        assert score1 == score2


# ─── Tone Grader Tests ────────────────────────────────────────────────────────

class TestGradeTone:

    def test_exact_match(self):
        assert grade_tone("apologetic", "apologetic", "angry") == 1.0

    def test_none_returns_neutral(self):
        score = grade_tone(None, "apologetic", "angry")
        assert score == 0.5

    def test_compatible_tones_partial_credit(self):
        score = grade_tone("empathetic", "apologetic", "angry")
        assert 0.0 < score < 1.0

    def test_formal_to_angry_customer_penalized(self):
        formal_score = grade_tone("formal", "apologetic", "angry")
        apologetic_score = grade_tone("apologetic", "apologetic", "angry")
        assert formal_score < apologetic_score

    def test_score_always_in_range(self):
        tones = [
            "empathetic", "formal", "apologetic",
            "informative", "friendly", "warm",
            "enthusiastic", "formal_apologetic"
        ]
        sentiments = ["neutral", "angry", "happy", "frustrated", "furious"]
        for pred in tones:
            for ideal in tones:
                for sentiment in sentiments:
                    score = grade_tone(pred, ideal, sentiment)
                    assert 0.0 <= score <= 1.0


# ─── Escalation Grader Tests ─────────────────────────────────────────────────

class TestGradeEscalation:

    def test_correct_escalation(self):
        """Escalate when required."""
        score = grade_escalation(True, True, 5)
        assert score == 1.0

    def test_correct_no_escalation(self):
        """Do not escalate when not required."""
        score = grade_escalation(False, False, 2)
        assert score == 1.0

    def test_false_alarm_penalized(self):
        """Escalating when not needed."""
        score = grade_escalation(True, False, 2)
        assert score == 0.2

    def test_missed_escalation_zero(self):
        """Not escalating when required."""
        score = grade_escalation(False, True, 5)
        assert score == 0.0

    def test_none_when_required_zero(self):
        """No escalation decision on required email."""
        score = grade_escalation(None, True, 5)
        assert score == 0.0

    def test_none_when_not_required_partial(self):
        """No escalation decision on normal email."""
        score = grade_escalation(None, False, 2)
        assert score == 0.8

    def test_score_always_in_range(self):
        for predicted in [True, False, None]:
            for required in [True, False]:
                for priority in [1, 2, 3, 4, 5]:
                    score = grade_escalation(predicted, required, priority)
                    assert 0.0 <= score <= 1.0


# ─── SLA Grader Tests ─────────────────────────────────────────────────────────

class TestGradeSlaHandling:

    def test_correct_sla_flag(self):
        """Correctly flagged SLA breach risk."""
        score = grade_sla_handling(True, True, 5, 5)
        assert score == 1.0

    def test_no_sla_risk_no_flag(self):
        """Correctly did not flag SLA."""
        score = grade_sla_handling(False, False, 2, 2)
        assert score == 1.0

    def test_missed_sla_flag(self):
        """Did not flag SLA when it was at risk."""
        score = grade_sla_handling(False, True, 3, 5)
        assert score < 1.0

    def test_false_sla_alarm(self):
        """Flagged SLA when no risk existed."""
        score = grade_sla_handling(True, False, 2, 2)
        assert score == 0.5

    def test_score_always_in_range(self):
        for marked in [True, False, None]:
            for risk in [True, False]:
                for pri in [1, 3, 5]:
                    score = grade_sla_handling(marked, risk, pri, pri)
                    assert 0.0 <= score <= 1.0


# ─── Task 1 Grader Tests ─────────────────────────────────────────────────────

class TestGradeInboxSort:

    def test_perfect_score(self):
        action = make_action(category="BILLING", priority=4)
        score, breakdown, feedback = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert score == 1.0
        assert breakdown.total == 1.0
        assert "✓" in feedback

    def test_wrong_category(self):
        action = make_action(category="INQUIRY", priority=4)
        score, breakdown, feedback = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert score < 1.0
        assert breakdown.category_score == 0.0

    def test_wrong_priority(self):
        action = make_action(category="BILLING", priority=1)
        score, breakdown, feedback = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert score < 1.0
        assert breakdown.priority_score == 0.0

    def test_both_wrong(self):
        action = make_action(category="SPAM", priority=1)
        score, breakdown, feedback = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert score == 0.0

    def test_score_always_in_range(self):
        categories = ["TECHNICAL", "BILLING", "SPAM", "INQUIRY"]
        priorities = [1, 2, 3, 4, 5]
        for cat in categories:
            for pri in priorities:
                action = make_action(category=cat, priority=pri)
                score, _, _ = grade_inbox_sort(action, EMAIL_GT_BILLING)
                assert 0.0 <= score <= 1.0

    def test_deterministic(self):
        action = make_action(category="BILLING", priority=4)
        score1, _, _ = grade_inbox_sort(action, EMAIL_GT_BILLING)
        score2, _, _ = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert score1 == score2

    def test_returns_feedback_string(self):
        action = make_action(category="BILLING", priority=4)
        _, _, feedback = grade_inbox_sort(action, EMAIL_GT_BILLING)
        assert isinstance(feedback, str)
        assert len(feedback) > 0


# ─── Task 2 Grader Tests ─────────────────────────────────────────────────────

class TestGradeInboxRoute:

    def test_perfect_score(self):
        action = make_action(
            email_id="email_001",
            category="BILLING",
            priority=4,
            route_to="billing",
            reply_draft=(
                "We sincerely apologize for the invoice error. "
                "Our billing team will send a corrected invoice "
                "and resolve this immediately."
            ),
            done=True,
        )
        score, breakdown, feedback = grade_inbox_route(action, EMAIL_GT_BILLING)
        assert score > 0.7
        assert 0.0 <= score <= 1.0

    def test_no_routing_penalized(self):
        action = make_action(
            category="BILLING",
            priority=4,
            route_to=None,
            done=True,
        )
        score_no_route, _, _ = grade_inbox_route(action, EMAIL_GT_BILLING)

        action_routed = make_action(
            category="BILLING",
            priority=4,
            route_to="billing",
            done=True,
        )
        score_routed, _, _ = grade_inbox_route(action_routed, EMAIL_GT_BILLING)
        assert score_routed > score_no_route

    def test_score_always_in_range(self):
        test_cases = [
            ("BILLING", 4, "billing", "We apologize for the invoice issue"),
            ("SPAM", 1, "close", None),
            ("TECHNICAL", 5, "engineering", "Escalated to engineering team"),
            ("INQUIRY", 2, "self", "Here is how to export your data"),
        ]
        for cat, pri, route, reply in test_cases:
            action = make_action(
                category=cat,
                priority=pri,
                route_to=route,
                reply_draft=reply,
                done=True,
            )
            score, _, _ = grade_inbox_route(action, EMAIL_GT_BILLING)
            assert 0.0 <= score <= 1.0

    def test_deterministic(self):
        action = make_action(
            category="BILLING",
            priority=4,
            route_to="billing",
            reply_draft="Apologies for the billing issue",
            done=True,
        )
        score1, _, _ = grade_inbox_route(action, EMAIL_GT_BILLING)
        score2, _, _ = grade_inbox_route(action, EMAIL_GT_BILLING)
        assert score1 == score2


# ─── Task 3 Grader Tests ─────────────────────────────────────────────────────

class TestGradeInboxCrisis:

    def test_perfect_action_high_score(self):
        action = make_action(
            email_id="email_005",
            category="TECHNICAL",
            priority=5,
            route_to="engineering",
            reply_draft=(
                "This is urgent. We have escalated to our engineering team "
                "and they are investigating this P0 priority issue immediately. "
                "We will provide an update in 30 minutes."
            ),
            reply_tone="apologetic",
            escalate=True,
            escalation_reason="Production down, P0 incident",
            mark_sla_breach_risk=True,
            done=True,
        )
        score, breakdown, feedback = grade_inbox_crisis(
            action, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        assert score > 0.70
        assert 0.0 <= score <= 1.0

    def test_spam_reply_penalized(self):
        action = make_action(
            email_id="email_003",
            category="SPAM",
            priority=1,
            route_to="close",
            reply_draft="Thank you for contacting us!",
            done=True,
        )
        score, breakdown, feedback = grade_inbox_crisis(
            action, EMAIL_GT_SPAM, THREAD_GT_NO_SLA
        )
        assert breakdown.penalty > 0
        assert 0.0 <= score <= 1.0

    def test_missed_escalation_hurts_score(self):
        action_escalated = make_action(
            email_id="email_005",
            category="TECHNICAL",
            priority=5,
            route_to="engineering",
            escalate=True,
            done=True,
        )
        action_no_escalate = make_action(
            email_id="email_005",
            category="TECHNICAL",
            priority=5,
            route_to="engineering",
            escalate=False,
            done=True,
        )
        score_esc, _, _ = grade_inbox_crisis(
            action_escalated, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        score_no_esc, _, _ = grade_inbox_crisis(
            action_no_escalate, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        assert score_esc > score_no_esc

    def test_score_always_in_range(self):
        """Exhaustive range check."""
        test_actions = [
            make_action(
                category="TECHNICAL", priority=5,
                route_to="engineering", escalate=True,
                mark_sla_breach_risk=True, done=True
            ),
            make_action(
                category="SPAM", priority=1,
                route_to="close", done=True
            ),
            make_action(
                category="BILLING", priority=3,
                route_to="billing", done=True
            ),
            make_action(
                category="COMPLAINT", priority=4,
                route_to="manager", escalate=False,
                done=True
            ),
        ]
        for action in test_actions:
            score, _, _ = grade_inbox_crisis(
                action, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
            )
            assert 0.0 <= score <= 1.0, f"Score out of range: {score}"

    def test_deterministic(self):
        action = make_action(
            category="TECHNICAL",
            priority=5,
            route_to="engineering",
            escalate=True,
            done=True,
        )
        score1, _, _ = grade_inbox_crisis(
            action, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        score2, _, _ = grade_inbox_crisis(
            action, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        assert score1 == score2

    def test_breakdown_components_sum_correctly(self):
        action = make_action(
            category="TECHNICAL",
            priority=5,
            route_to="engineering",
            escalate=True,
            mark_sla_breach_risk=True,
            done=True,
        )
        score, breakdown, _ = grade_inbox_crisis(
            action, EMAIL_GT_TECHNICAL, THREAD_GT_SLA
        )
        assert breakdown.total == score
        assert 0.0 <= breakdown.category_score <= 1.0
        assert 0.0 <= breakdown.priority_score <= 1.0
        assert 0.0 <= breakdown.routing_score <= 1.0
        assert 0.0 <= breakdown.escalation_score <= 1.0
        assert 0.0 <= breakdown.sla_score <= 1.0