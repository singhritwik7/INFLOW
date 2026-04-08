# env/inboxflow_env.py
"""
Main InboxFlow environment.
Implements the OpenEnv interface: reset(), step(), state(), close()
"""

import copy
from typing import Dict, Any, List, Optional, Tuple

from env.models import (
    InboxObservation,
    InboxAction,
    InboxReward,
    StepResult,
    ResetResult,
    CustomerProfile,
    EmailData,
    ThreadInfo,
    InboxSummary,
)
from env.tasks import get_task, TASK_REGISTRY
from env.reward import compute_reward, compute_episode_bonus
from env.data.emails import get_email, get_emails_by_thread
from env.data.customers import get_customer
from env.data.threads import get_thread, get_thread_for_email


class InboxFlowEnv:
    """
    InboxFlow: Intelligent Customer Inbox Triage Environment.

    Simulates a real customer support inbox with:
    - Thread-aware email context
    - Customer profiles and history
    - SLA breach detection
    - Shaped reward function
    - 3 difficulty levels

    Usage:
        env = InboxFlowEnv(task_name="inbox-sort")
        obs = env.reset()
        result = env.step(action)
        state = env.state()
        env.close()
    """

    ENV_NAME = "inboxflow"
    VERSION = "1.0.0"

    def __init__(self, task_name: str = "inbox-sort"):
        if task_name not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task '{task_name}'. "
                f"Available: {list(TASK_REGISTRY.keys())}"
            )

        self.task_name = task_name
        self.task_config = get_task(task_name)

        # State variables — reset on each reset() call
        self._email_ids: List[str] = []
        self._current_email_index: int = 0
        self._step_count: int = 0
        self._done: bool = False
        self._total_score: float = 0.0
        self._rewards_history: List[float] = []
        self._actions_history: List[Dict[str, Any]] = []
        self._processed_emails: List[str] = []
        self._escalations_correct: int = 0
        self._escalations_total: int = 0
        self._sla_handled: int = 0
        self._sla_total: int = 0
        self._last_feedback: str = ""
        self._last_error: Optional[str] = None
        self._initialized: bool = False

    # ─── PUBLIC API ──────────────────────────────────────────────────────────

    def reset(self) -> ResetResult:
        """
        Reset environment to initial state.
        Returns first email observation.
        """
        # Load email IDs for this task
        self._email_ids = list(self.task_config["email_ids"])
        self._current_email_index = 0
        self._step_count = 0
        self._done = False
        self._total_score = 0.0
        self._rewards_history = []
        self._actions_history = []
        self._processed_emails = []
        self._escalations_correct = 0
        self._escalations_total = 0
        self._sla_handled = 0
        self._sla_total = 0
        self._last_feedback = ""
        self._last_error = None
        self._initialized = True

        # Count SLA emails
        for eid in self._email_ids:
            email_gt = get_email(eid)
            thread_gt = get_thread_for_email(eid)
            if thread_gt.get("is_sla_breach_risk"):
                self._sla_total += 1

        obs = self._build_observation()

        return ResetResult(
            observation=obs,
            done=False,
            info={
                "task": self.task_name,
                "total_emails": len(self._email_ids),
                "max_steps": self.task_config["max_steps"],
            }
        )

    def step(self, action: InboxAction) -> StepResult:
        """
        Process one action on the current email.
        Returns next observation, reward, done flag, and info.
        """
        if not self._initialized:
            raise RuntimeError("Call reset() before step()")

        if self._done:
            raise RuntimeError(
                "Episode is done. Call reset() to start new episode."
            )

        self._step_count += 1
        self._last_error = None

        # Validate email_id matches current email
        current_email_id = self._email_ids[self._current_email_index]
        if action.email_id != current_email_id:
            self._last_error = (
                f"email_id mismatch: got '{action.email_id}' "
                f"expected '{current_email_id}'"
            )
            # Penalize but don't crash
            reward_value = 0.0
            self._rewards_history.append(reward_value)
            obs = self._build_observation()
            obs.last_action_error = self._last_error
            return StepResult(
                observation=obs,
                reward=reward_value,
                done=self._done,
                info={"error": self._last_error}
            )

        # Get ground truth for this email
        email_gt = get_email(current_email_id)
        thread_gt = get_thread_for_email(current_email_id)

        # Compute reward
        try:
            reward_obj: InboxReward = compute_reward(
                task_name=self.task_name,
                action=action,
                email_gt=email_gt,
                thread_gt=thread_gt,
                step=self._step_count,
                max_steps=self.task_config["max_steps"],
            )
        except Exception as e:
            self._last_error = f"Reward computation error: {str(e)}"
            reward_obj = InboxReward(
                value=0.0,
                breakdown=__import__(
                    "env.models", fromlist=["RewardBreakdown"]
                ).RewardBreakdown(),
                feedback=self._last_error,
            )

        reward_value = reward_obj.value
        self._rewards_history.append(reward_value)
        self._last_feedback = reward_obj.feedback

        # Track escalation accuracy
        if email_gt.get("requires_escalation"):
            self._escalations_total += 1
            if action.escalate:
                self._escalations_correct += 1

        # Track SLA handling
        if thread_gt.get("is_sla_breach_risk"):
            if action.mark_sla_breach_risk or action.priority >= 4:
                self._sla_handled += 1

        # Record action
        self._actions_history.append({
            "step": self._step_count,
            "email_id": current_email_id,
            "action": action.model_dump(),
            "reward": reward_value,
            "feedback": self._last_feedback,
        })

        # Mark email processed
        self._processed_emails.append(current_email_id)

        # Advance to next email if agent says done with this one
        if action.done:
            self._current_email_index += 1

        # Check episode done conditions
        episode_done = False

        # All emails processed
        if self._current_email_index >= len(self._email_ids):
            episode_done = True

        # Max steps reached
        if self._step_count >= self.task_config["max_steps"]:
            episode_done = True

        if episode_done:
            self._done = True
            self._total_score = self._compute_final_score()

        # Build next observation
        if not self._done and self._current_email_index < len(self._email_ids):
            obs = self._build_observation()
        else:
            # Final observation — use last email
            obs = self._build_final_observation()

        obs.score_so_far = (
            sum(self._rewards_history) / len(self._rewards_history)
            if self._rewards_history else 0.0
        )
        obs.last_action_feedback = self._last_feedback
        obs.last_action_error = self._last_error

        return StepResult(
            observation=obs,
            reward=reward_value,
            done=self._done,
            info={
                "step": self._step_count,
                "email_id": current_email_id,
                "reward_breakdown": reward_obj.breakdown.model_dump(),
                "feedback": self._last_feedback,
                "emails_remaining": max(
                    0,
                    len(self._email_ids) - self._current_email_index
                ),
                "final_score": self._total_score if self._done else None,
                "error": self._last_error,
            }
        )

    def state(self) -> Dict[str, Any]:
        """
        Return current environment state.
        Used by openenv validate and monitoring.
        """
        if not self._initialized:
            return {"initialized": False}

        current_email_id = (
            self._email_ids[self._current_email_index]
            if self._current_email_index < len(self._email_ids)
            else None
        )

        return {
            "env": self.ENV_NAME,
            "version": self.VERSION,
            "task": self.task_name,
            "step": self._step_count,
            "max_steps": self.task_config["max_steps"],
            "current_email_id": current_email_id,
            "current_email_index": self._current_email_index,
            "total_emails": len(self._email_ids),
            "processed_emails": len(self._processed_emails),
            "emails_remaining": max(
                0,
                len(self._email_ids) - self._current_email_index
            ),
            "done": self._done,
            "total_score": self._total_score,
            "rewards_history": self._rewards_history,
            "average_reward": (
                sum(self._rewards_history) / len(self._rewards_history)
                if self._rewards_history else 0.0
            ),
            "escalations_correct": self._escalations_correct,
            "escalations_total": self._escalations_total,
            "sla_handled": self._sla_handled,
            "sla_total": self._sla_total,
            "last_feedback": self._last_feedback,
            "last_error": self._last_error,
            "initialized": self._initialized,
        }

    def close(self) -> None:
        """Clean up environment resources."""
        self._initialized = False

    # ─── PRIVATE HELPERS ─────────────────────────────────────────────────────

    def _build_observation(self) -> InboxObservation:
        """Build observation for current email."""
        current_email_id = self._email_ids[self._current_email_index]
        email_raw = get_email(current_email_id)
        thread_raw = get_thread_for_email(current_email_id)
        customer_raw = get_customer(email_raw["customer_id"])

        # Build EmailData model
        current_email = EmailData(
            id=email_raw["id"],
            subject=email_raw["subject"],
            body=email_raw["body"],
            sender_email=email_raw["sender_email"],
            customer_id=email_raw["customer_id"],
            timestamp=email_raw["timestamp"],
            thread_id=email_raw["thread_id"],
            is_thread_starter=email_raw["is_thread_starter"],
            sentiment=email_raw.get("sentiment", "neutral"),
            sla_hours=email_raw.get("sla_hours"),
        )

        # Build thread history
        thread_history = []
        if thread_raw:
            all_thread_emails = get_emails_by_thread(email_raw["thread_id"])
            for te in all_thread_emails:
                if te["id"] != current_email_id:
                    thread_history.append(EmailData(
                        id=te["id"],
                        subject=te["subject"],
                        body=te["body"],
                        sender_email=te["sender_email"],
                        customer_id=te["customer_id"],
                        timestamp=te["timestamp"],
                        thread_id=te["thread_id"],
                        is_thread_starter=te["is_thread_starter"],
                        sentiment=te.get("sentiment", "neutral"),
                        sla_hours=te.get("sla_hours"),
                    ))

        # Build ThreadInfo
        thread_info = None
        if thread_raw:
            thread_info = ThreadInfo(
                id=thread_raw["id"],
                subject=thread_raw["subject"],
                status=thread_raw["status"],
                sla_deadline=thread_raw.get("sla_deadline"),
                is_sla_breach_risk=thread_raw.get("is_sla_breach_risk", False),
                thread_sentiment_trend=thread_raw.get(
                    "thread_sentiment_trend", "stable"
                ),
                context_summary=thread_raw.get("context_summary", ""),
                email_count=len(thread_raw.get("email_ids", [])),
            )

        # Build CustomerProfile
        customer_profile = CustomerProfile(
            id=customer_raw["id"],
            name=customer_raw["name"],
            email=customer_raw["email"],
            company=customer_raw["company"],
            plan=customer_raw["plan"],
            mrr=customer_raw["mrr"],
            account_age_days=customer_raw["account_age_days"],
            open_tickets=customer_raw["open_tickets"],
            sentiment_history=customer_raw["sentiment_history"],
            last_sentiment=customer_raw["last_sentiment"],
            sla_tier=customer_raw["sla_tier"],
            tags=customer_raw["tags"],
            notes=customer_raw["notes"],
        )

        # Build InboxSummary
        remaining = len(self._email_ids) - self._current_email_index
        urgent_count = sum(
            1 for eid in self._email_ids[self._current_email_index:]
            if get_email(eid).get("true_priority", 0) >= 4
        )
        sla_risk_count = sum(
            1 for eid in self._email_ids[self._current_email_index:]
            if get_thread_for_email(eid).get("is_sla_breach_risk", False)
        )

        inbox_summary = InboxSummary(
            total_emails=len(self._email_ids),
            processed=len(self._processed_emails),
            remaining=remaining,
            urgent_count=urgent_count,
            sla_breach_risk_count=sla_risk_count,
            categories_seen=list(set(
                a["action"].get("category", "")
                for a in self._actions_history
                if a["action"].get("category")
            )),
        )

        return InboxObservation(
            current_email=current_email,
            thread_history=thread_history,
            thread_info=thread_info,
            customer_profile=customer_profile,
            inbox_summary=inbox_summary,
            task_name=self.task_name,
            step=self._step_count,
            max_steps=self.task_config["max_steps"],
            instruction=self.task_config["instruction"],
            sla_deadline=thread_raw.get("sla_deadline") if thread_raw else None,
            sla_breach_risk=(
                thread_raw.get("is_sla_breach_risk", False)
                if thread_raw else False
            ),
            last_action_feedback=self._last_feedback,
            score_so_far=(
                sum(self._rewards_history) / len(self._rewards_history)
                if self._rewards_history else 0.0
            ),
            available_actions=self.task_config["available_actions"],
            last_action_error=self._last_error,
        )

    def _build_final_observation(self) -> InboxObservation:
        """Build observation for end of episode."""
        # Use last processed email for final obs
        last_email_id = (
            self._email_ids[-1]
            if self._email_ids
            else self._email_ids[0]
        )
        email_raw = get_email(last_email_id)
        thread_raw = get_thread_for_email(last_email_id)
        customer_raw = get_customer(email_raw["customer_id"])

        current_email = EmailData(
            id=email_raw["id"],
            subject=email_raw["subject"],
            body=email_raw["body"],
            sender_email=email_raw["sender_email"],
            customer_id=email_raw["customer_id"],
            timestamp=email_raw["timestamp"],
            thread_id=email_raw["thread_id"],
            is_thread_starter=email_raw["is_thread_starter"],
            sentiment=email_raw.get("sentiment", "neutral"),
            sla_hours=email_raw.get("sla_hours"),
        )

        customer_profile = CustomerProfile(
            id=customer_raw["id"],
            name=customer_raw["name"],
            email=customer_raw["email"],
            company=customer_raw["company"],
            plan=customer_raw["plan"],
            mrr=customer_raw["mrr"],
            account_age_days=customer_raw["account_age_days"],
            open_tickets=customer_raw["open_tickets"],
            sentiment_history=customer_raw["sentiment_history"],
            last_sentiment=customer_raw["last_sentiment"],
            sla_tier=customer_raw["sla_tier"],
            tags=customer_raw["tags"],
            notes=customer_raw["notes"],
        )

        inbox_summary = InboxSummary(
            total_emails=len(self._email_ids),
            processed=len(self._processed_emails),
            remaining=0,
            urgent_count=0,
            sla_breach_risk_count=0,
            categories_seen=list(set(
                a["action"].get("category", "")
                for a in self._actions_history
                if a["action"].get("category")
            )),
        )

        return InboxObservation(
            current_email=current_email,
            thread_history=[],
            thread_info=None,
            customer_profile=customer_profile,
            inbox_summary=inbox_summary,
            task_name=self.task_name,
            step=self._step_count,
            max_steps=self.task_config["max_steps"],
            instruction="Episode complete.",
            sla_deadline=None,
            sla_breach_risk=False,
            last_action_feedback=self._last_feedback,
            score_so_far=self._total_score,
            available_actions=[],
            last_action_error=self._last_error,
        )

    def _compute_final_score(self) -> float:
        """
        Compute final episode score with end-of-episode bonuses.
        Always returns value in [0.0, 1.0].
        """
        if not self._rewards_history:
            return 0.0

        base_score = sum(self._rewards_history) / len(self._rewards_history)

        all_escalations_correct = (
            self._escalations_correct == self._escalations_total
            if self._escalations_total > 0 else True
        )
        all_sla_handled = (
            self._sla_handled >= self._sla_total * 0.8
            if self._sla_total > 0 else True
        )
        inbox_cleared = (
            len(self._processed_emails) >= len(self._email_ids)
        )

        bonus = compute_episode_bonus(
            task_name=self.task_name,
            step_rewards=self._rewards_history,
            all_escalations_correct=all_escalations_correct,
            all_sla_handled=all_sla_handled,
            inbox_cleared=inbox_cleared,
        )

        final = min(1.0, max(0.0, base_score + bonus))
        return round(final, 4)