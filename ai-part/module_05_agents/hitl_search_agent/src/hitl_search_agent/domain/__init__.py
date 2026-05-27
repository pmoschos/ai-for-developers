"""
hitl_search_agent.domain
~~~~~~~~~~~~~~~~~~~~~~~~

Domain layer — state definitions and Pydantic models.
"""

from hitl_search_agent.domain.state import HITLSearchState, HumanDecision, make_initial_state
from hitl_search_agent.domain.models import ProposalOutput

__all__ = [
    "HITLSearchState",
    "HumanDecision",
    "make_initial_state",
    "ProposalOutput",
]
