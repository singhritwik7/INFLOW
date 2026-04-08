# tests/test_server.py
"""
Tests for FastAPI server endpoints.
Tests all OpenEnv required endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


# ─── Health Tests ─────────────────────────────────────────────────────────────

class TestHealth:

    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok(self):
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"

    def test_health_returns_env_name(self):
        resp = client.get("/health")
        data = resp.json()
        assert data["env"] == "inboxflow"

    def test_health_returns_tasks(self):
        resp = client.get("/health")
        data = resp.json()
        assert "tasks" in data
        assert len(data["tasks"]) == 3


# ─── Reset Tests ──────────────────────────────────────────────────────────────

class TestReset:

    def test_reset_returns_200(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        assert resp.status_code == 200

    def test_reset_returns_observation(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        data = resp.json()
        assert "observation" in data
        assert "done" in data

    def test_reset_observation_has_email(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        obs = resp.json()["observation"]
        assert "current_email" in obs
        assert obs["current_email"]["id"] == "email_001"

    def test_reset_observation_has_customer(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        obs = resp.json()["observation"]
        assert "customer_profile" in obs
        assert obs["customer_profile"]["name"] == "Sarah Chen"

    def test_reset_observation_has_instruction(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        obs = resp.json()["observation"]
        assert "instruction" in obs
        assert len(obs["instruction"]) > 0

    def test_reset_all_tasks(self):
        for task in ["inbox-sort", "inbox-route", "inbox-crisis"]:
            resp = client.post(
                "/reset",
                json={"task_name": task}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["observation"]["task_name"] == task

    def test_reset_invalid_task_returns_400(self):
        resp = client.post(
            "/reset",
            json={"task_name": "nonexistent-task"}
        )
        assert resp.status_code == 400

    def test_reset_done_is_false(self):
        resp = client.post(
            "/reset",
            json={"task_name": "inbox-sort"}
        )
        assert resp.json()["done"] is False


# ─── Step Tests ───────────────────────────────────────────────────────────────

class TestStep:

    def setup_method(self):
        """Reset environment before each test."""
        client.post("/reset", json={"task_name": "inbox-sort"})

    def test_step_returns_200(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        assert resp.status_code == 200

    def test_step_returns_reward(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        data = resp.json()
        assert "reward" in data
        assert 0.0 <= data["reward"] <= 1.0

    def test_step_returns_observation(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        data = resp.json()
        assert "observation" in data

    def test_step_returns_done_flag(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        data = resp.json()
        assert "done" in data
        assert isinstance(data["done"], bool)

    def test_step_reward_in_range(self):
        """Reward must always be in [0.0, 1.0]."""
        test_actions = [
            {"email_id": "email_001", "category": "BILLING",
             "priority": 4, "done": True},
            {"email_id": "email_001", "category": "SPAM",
             "priority": 1, "done": True},
            {"email_id": "email_001", "category": "TECHNICAL",
             "priority": 5, "done": True},
        ]
        for action in test_actions:
            client.post("/reset", json={"task_name": "inbox-sort"})
            resp = client.post("/step", json=action)
            assert resp.status_code == 200
            reward = resp.json()["reward"]
            assert 0.0 <= reward <= 1.0, (
                f"Reward out of range: {reward} for action {action}"
            )

    def test_perfect_action_high_reward(self):
        """Correct category and priority gives high reward."""
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        assert resp.json()["reward"] >= 0.8

    def test_wrong_action_low_reward(self):
        """Wrong category and priority gives low reward."""
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "SPAM",
            "priority": 1,
            "done": True,
        })
        assert resp.json()["reward"] < 0.5

    def test_step_without_reset_returns_400(self):
        """Step without reset should fail."""
        # Force no env
        import server
        server._env = None
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        assert resp.status_code == 400
        # Reset for other tests
        client.post("/reset", json={"task_name": "inbox-sort"})

    def test_invalid_category_returns_422(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "INVALID_CATEGORY",
            "priority": 4,
            "done": True,
        })
        assert resp.status_code == 422

    def test_invalid_priority_returns_422(self):
        resp = client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 99,
            "done": True,
        })
        assert resp.status_code == 422

    def test_full_episode_inbox_sort(self):
        """Run complete inbox-sort episode."""
        client.post("/reset", json={"task_name": "inbox-sort"})

        actions = [
            {"email_id": "email_001", "category": "BILLING",
             "priority": 4, "done": True},
            {"email_id": "email_002", "category": "INQUIRY",
             "priority": 2, "done": True},
            {"email_id": "email_003", "category": "SPAM",
             "priority": 1, "done": True},
            {"email_id": "email_004", "category": "COMPLIMENT",
             "priority": 2, "done": True},
            {"email_id": "email_005", "category": "TECHNICAL",
             "priority": 5, "done": True},
        ]

        rewards = []
        done = False

        for action in actions:
            if done:
                break
            resp = client.post("/step", json=action)
            assert resp.status_code == 200
            data = resp.json()
            rewards.append(data["reward"])
            done = data["done"]
            assert 0.0 <= data["reward"] <= 1.0

        assert done is True
        assert len(rewards) > 0


# ─── State Tests ──────────────────────────────────────────────────────────────

class TestState:

    def test_state_returns_200(self):
        resp = client.get("/state")
        assert resp.status_code == 200

    def test_state_before_reset(self):
        import server
        server._env = None
        resp = client.get("/state")
        assert resp.status_code == 200
        data = resp.json()
        assert data["initialized"] is False

    def test_state_after_reset(self):
        client.post("/reset", json={"task_name": "inbox-sort"})
        resp = client.get("/state")
        data = resp.json()
        assert data["initialized"] is True
        assert data["task"] == "inbox-sort"

    def test_state_tracks_steps(self):
        client.post("/reset", json={"task_name": "inbox-sort"})
        client.post("/step", json={
            "email_id": "email_001",
            "category": "BILLING",
            "priority": 4,
            "done": True,
        })
        resp = client.get("/state")
        data = resp.json()
        assert data["step"] == 1
        assert data["processed_emails"] == 1

    def test_state_has_required_fields(self):
        client.post("/reset", json={"task_name": "inbox-sort"})
        resp = client.get("/state")
        data = resp.json()
        required_fields = [
            "task", "step", "max_steps", "done",
            "total_score", "rewards_history",
            "initialized", "env"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


# ─── Tasks Endpoint Tests ─────────────────────────────────────────────────────

class TestTasksEndpoint:

    def test_tasks_returns_200(self):
        resp = client.get("/tasks")
        assert resp.status_code == 200

    def test_tasks_returns_three_tasks(self):
        resp = client.get("/tasks")
        data = resp.json()
        assert len(data["tasks"]) == 3

    def test_tasks_have_required_fields(self):
        resp = client.get("/tasks")
        for task in resp.json()["tasks"]:
            assert "name" in task
            assert "difficulty" in task
            assert "max_steps" in task
            assert "score_range" in task
            assert task["score_range"] == [0.0, 1.0]

    def test_tasks_difficulty_progression(self):
        resp = client.get("/tasks")
        tasks = resp.json()["tasks"]
        difficulties = [t["difficulty"] for t in tasks]
        assert "easy" in difficulties
        assert "medium" in difficulties
        assert "hard" in difficulties


# ─── OpenEnv YAML Endpoint ────────────────────────────────────────────────────

class TestOpenEnvYaml:

    def test_yaml_returns_200(self):
        resp = client.get("/openenv.yaml")
        assert resp.status_code == 200

    def test_yaml_has_content(self):
        resp = client.get("/openenv.yaml")
        assert len(resp.text) > 100