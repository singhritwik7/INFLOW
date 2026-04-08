# server.py
"""
FastAPI server exposing InboxFlow environment as HTTP API.
Implements OpenEnv standard endpoints.
"""

import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import uvicorn

from env.inboxflow_env import InboxFlowEnv
from env.models import InboxAction
from env.tasks import list_tasks, TASK_REGISTRY

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="InboxFlow — OpenEnv Email Triage Environment",
    description=(
        "Real-world customer support inbox triage environment. "
        "AI agents learn to categorize, prioritize, route, and "
        "reply to emails with thread awareness and SLA pressure."
    ),
    version="1.0.0",
)

# Global environment instance
# In production this would be session-based
_env: Optional[InboxFlowEnv] = None


# ─── Request/Response Models ──────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_name: str = "inbox-sort"


class StepRequest(BaseModel):
    email_id: str
    category: str
    priority: int
    done: bool
    route_to: Optional[str] = None
    reply_draft: Optional[str] = None
    reply_tone: Optional[str] = None
    escalate: Optional[bool] = None
    escalation_reason: Optional[str] = None
    snooze_hours: Optional[int] = None
    merge_with_thread: Optional[str] = None
    mark_sla_breach_risk: Optional[bool] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "env": "inboxflow",
        "version": "1.0.0",
        "tasks": list_tasks(),
    }


@app.post("/reset")
async def reset(request: ResetRequest) -> Dict[str, Any]:
    """
    Reset environment and return initial observation.
    Required by OpenEnv spec.
    """
    global _env

    if request.task_name not in TASK_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown task '{request.task_name}'. "
                f"Available: {list_tasks()}"
            )
        )

    _env = InboxFlowEnv(task_name=request.task_name)
    result = _env.reset()

    return {
        "observation": result.observation.model_dump(),
        "done": result.done,
        "info": result.info,
    }


@app.post("/step")
async def step(request: StepRequest) -> Dict[str, Any]:
    """
    Take one action in the environment.
    Required by OpenEnv spec.
    """
    global _env

    if _env is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first."
        )

    try:
        action = InboxAction(
            email_id=request.email_id,
            category=request.category,
            priority=request.priority,
            done=request.done,
            route_to=request.route_to,
            reply_draft=request.reply_draft,
            reply_tone=request.reply_tone,
            escalate=request.escalate,
            escalation_reason=request.escalation_reason,
            snooze_hours=request.snooze_hours,
            merge_with_thread=request.merge_with_thread,
            mark_sla_breach_risk=request.mark_sla_breach_risk,
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action: {str(e)}"
        )

    try:
        result = _env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "observation": result.observation.model_dump(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
async def state() -> Dict[str, Any]:
    """
    Return current environment state.
    Required by OpenEnv spec.
    """
    global _env

    if _env is None:
        return {"initialized": False, "env": "inboxflow"}

    return _env.state()


@app.get("/tasks")
async def tasks() -> Dict[str, Any]:
    """List all available tasks."""
    return {
        "tasks": [
            {
                "name": t["name"],
                "display_name": t["display_name"],
                "difficulty": t["difficulty"],
                "description": t["description"],
                "max_steps": t["max_steps"],
                "success_threshold": t["success_threshold"],
                "score_range": [0.0, 1.0],
            }
            for t in TASK_REGISTRY.values()
        ]
    }


@app.get("/openenv.yaml", response_class=PlainTextResponse)
async def openenv_yaml() -> str:
    """Serve openenv.yaml spec file."""
    yaml_path = os.path.join(os.path.dirname(__file__), "openenv.yaml")
    try:
        with open(yaml_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="openenv.yaml not found")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
        log_level="info",
    )