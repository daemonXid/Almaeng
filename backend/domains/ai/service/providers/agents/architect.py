from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from .base import AgentContext, get_pydantic_ai_model

if TYPE_CHECKING:
    from pydantic_ai import RunContext


def _create_architect_agent() -> Agent[AgentContext, str]:
    """Factory to create the architect agent lazily."""
    agent = Agent(
        get_pydantic_ai_model(),
        deps_type=AgentContext,
        system_prompt=(
            "You are the DAEMON Architect, an expert in the DAEMON System and high-performance Django architecture. "
            "Your goal is to help users build modular, efficient, and AI-first applications. "
            "Follow the 'Zen of xid' philosophy: simple over complex, strict modularity, and vertical slicing. "
            "Provide professional, concise, and helpful advice."
        ),
    )

    @agent.tool
    async def get_project_info(ctx: RunContext[AgentContext]) -> str:
        """Get basic info about the current project context."""
        return f"Project context: {ctx.deps.project_context}"

    return agent


# Lazy initialization to avoid import-time API calls
_architect_agent: Agent[AgentContext, str] | None = None


def get_architect_agent() -> Agent[AgentContext, str]:
    """Get or create the architect agent."""
    global _architect_agent
    if _architect_agent is None:
        _architect_agent = _create_architect_agent()
    return _architect_agent
