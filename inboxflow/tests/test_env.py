# tests/test_env.py
"""Basic environment tests."""

import pytest
from env.inboxflow_env import InboxFlowEnv
from env.models import InboxAction


def test_reset_returns_observation():
    env = InboxFlowEnv("inbox-sort")
    result = env.reset()
    assert result.observation is not None
    assert result.observation.current_email.id == "email_001"
    assert result.done is False


def test_step_returns_reward_in_range():
    env = InboxFlowEnv("inbox-sort")
    env.reset()
    action = InboxAction(
        email_id="email_001",
        category="BILLING",
        priority=4,
        done=True,
    )
    result = env.step(action)
    assert 0.0 <= result.reward <= 1.0
    assert result.observation is not None


def test_episode_completes():
    env = InboxFlowEnv("inbox-sort")
    env.reset()
    email_ids = ["email_001", "email_002", "email_003", "email_004", "email_005"]
    categories = ["BILLING", "INQUIRY", "SPAM", "COMPLIMENT", "TECHNICAL"]
    priorities = [4, 2, 1, 2, 5]

    done = False
    for i, (eid, cat, pri) in enumerate(
        zip(email_ids, categories, priorities)
    ):
        if done:
            break
        action = InboxAction(
            email_id=eid,
            category=cat,
            priority=pri,
            done=True,
        )
        result = env.step(action)
        done = result.done

    assert done is True


def test_state_returns_dict():
    env = InboxFlowEnv("inbox-sort")
    env.reset()
    state = env.state()
    assert isinstance(state, dict)
    assert state["task"] == "inbox-sort"
    assert state["initialized"] is True


def test_all_tasks_init():
    for task in ["inbox-sort", "inbox-route", "inbox-crisis"]:
        env = InboxFlowEnv(task)
        result = env.reset()
        assert result.observation is not None
        env.close()


def test_score_in_range():
    env = InboxFlowEnv("inbox-sort")
    env.reset()
    rewards = []
    email_ids = ["email_001", "email_002", "email_003", "email_004", "email_005"]
    for eid in email_ids:
        action = InboxAction(
            email_id=eid,
            category="INQUIRY",
            priority=3,
            done=True,
        )
        result = env.step(action)
        rewards.append(result.reward)
        if result.done:
            break

    state = env.state()
    assert 0.0 <= state["total_score"] <= 1.0