#!/usr/bin/env python3
import os
import json
from typing import List, Optional, Dict, Any

import httpx
from openai import OpenAI

# ─── REQUIRED CONFIG (STRICT) ────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")  # ❗ NO DEFAULT (IMPORTANT)

ENV_URL = os.getenv("INBOXFLOW_URL", "http://localhost:7860")

BENCHMARK = "inboxflow"
TASKS = ["inbox-sort", "inbox-route", "inbox-crisis"]

SUCCESS_THRESHOLD = 0.60
TEMPERATURE = 0.2
MAX_TOKENS = 300

# ─── LOGGING (STRICT FORMAT) ────────────────────────────────────────────────

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_clean = action.replace("\n", " ").replace("\r", "")
    print(f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

# ─── ENV CLIENT ─────────────────────────────────────────────────────────────

class InboxFlowClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def reset(self, task_name: str):
        return self.client.post(f"{self.base_url}/reset", json={"task_name": task_name}).json()

    def step(self, action_dict: Dict[str, Any]):
        return self.client.post(f"{self.base_url}/step", json=action_dict).json()

    def close(self):
        self.client.close()

# ─── SIMPLE PROMPT (FAST + SAFE) ─────────────────────────────────────────────

SYSTEM_PROMPT = "Return ONLY valid JSON."

def build_user_prompt(obs: Dict[str, Any]) -> str:
    email = obs.get("current_email", {})

    return f"""
Email ID: {email.get('id')}
Subject: {email.get('subject')}
Body: {email.get('body')}

Return JSON:
{{
 "email_id": "{email.get('id')}",
 "category": "INQUIRY",
 "priority": 3,
 "done": true
}}
"""

# ─── LLM CALL ───────────────────────────────────────────────────────────────

def get_llm_action(client: OpenAI, obs: Dict[str, Any]) -> Dict[str, Any]:
    email_id = obs.get("current_email", {}).get("id", "unknown")

    try:
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(obs)},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )

        raw = (res.choices[0].message.content or "").strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        action = json.loads(raw)

        action.setdefault("email_id", email_id)
        action.setdefault("category", "INQUIRY")
        action.setdefault("priority", 3)
        action.setdefault("done", True)

        return action

    except:
        return {
            "email_id": email_id,
            "category": "INQUIRY",
            "priority": 3,
            "done": True,
        }

# ─── RUN TASK ───────────────────────────────────────────────────────────────

def run_task(task_name: str, llm_client: OpenAI, env_client: InboxFlowClient):
    rewards = []
    steps = 0

    log_start(task_name, BENCHMARK, MODEL_NAME)

    try:
        reset_data = env_client.reset(task_name)
        obs = reset_data["observation"]
        done = False

        while not done and steps < 20:
            steps += 1

            action = get_llm_action(llm_client, obs)
            action_str = json.dumps(action, separators=(",", ":"))

            result = env_client.step(action)

            reward = result.get("reward", 0.0)
            done = result.get("done", False)
            obs = result.get("observation", obs)

            rewards.append(reward)

            log_step(steps, action_str, reward, done, None)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = max(0.0, min(1.0, score))
        success = score >= SUCCESS_THRESHOLD

    except:
        score = 0.0
        success = False

    log_end(success, steps, score, rewards)
    return score

# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN  # ❗ STRICT
    )

    env = InboxFlowClient(ENV_URL)

    # health check
    try:
        httpx.get(f"{ENV_URL}/health", timeout=5.0).raise_for_status()
    except:
        print("[ERROR] ENV NOT RUNNING", flush=True)
        return

    scores = []

    for task in TASKS:
        score = run_task(task, client, env)
        scores.append(score)

    overall = sum(scores) / len(scores) if scores else 0.0

    print(f"[SUMMARY] tasks=3 scores={','.join(f'{s:.2f}' for s in scores)} overall={overall:.2f}", flush=True)

    env.close()

if __name__ == "__main__":
    main()