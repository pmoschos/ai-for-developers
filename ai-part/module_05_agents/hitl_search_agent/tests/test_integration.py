"""
Integration tests for the HITL Search Agent.

End-to-end tests that run the full unified graph including the
interrupt/resume cycle, with mocked LLM and Tavily.
"""

from unittest.mock import patch, MagicMock

from hitl_search_agent.domain.models import ProposalOutput
from hitl_search_agent.domain.state import make_initial_state


class TestFullApproveFlow:
    """
    Test the complete approve flow:
    invoke → interrupt → resume with approve → get results
    """

    @patch("hitl_search_agent.graph.nodes._get_web_search_tool")
    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_full_approve_flow(self, mock_get_llm, mock_get_tool):
        """End-to-end: proposal → approve → search → summary."""
        # Setup LLM mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        # Structured output for proposal
        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = ProposalOutput(
            search_query="LangGraph HITL 2025",
            proposed_action="Search for LangGraph human-in-the-loop features.",
        )

        # Summary LLM response
        mock_summary_response = MagicMock()
        mock_summary_response.content = "LangGraph now supports native HITL via interrupt()."
        mock_llm.invoke.return_value = mock_summary_response

        # Setup Tavily mock
        mock_tool = MagicMock()
        mock_get_tool.return_value = mock_tool
        mock_tool.invoke.return_value = {
            "images": ["http://img1.png"],
            "results": [{"title": "Result 1", "content": "Content 1"}],
        }

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()

        # Phase 1: Generate proposal (runs until interrupt)
        state, thread_id = service.generate_proposal("Show me LangGraph HITL features")

        assert state["search_query"] == "LangGraph HITL 2025"
        assert state["proposed_action"] == "Search for LangGraph human-in-the-loop features."
        assert thread_id

        # Phase 2: Resume with approval
        result = service.resume_with_decision(
            thread_id=thread_id,
            decision={
                "approved": True,
                "edited_query": "LangGraph HITL 2025",
                "feedback": "Looks good, proceed.",
            },
        )

        assert result["approved"] is True
        assert result["search_query"] == "LangGraph HITL 2025"
        assert result["result"] == "LangGraph now supports native HITL via interrupt()."
        assert result["image_urls"] == ["http://img1.png"]


class TestFullRejectFlow:
    """
    Test the complete reject flow:
    invoke → interrupt → resume with reject → END
    """

    @patch("hitl_search_agent.graph.nodes._get_web_search_tool")
    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_full_reject_flow(self, mock_get_llm, mock_get_tool):
        """End-to-end: proposal → reject → no search."""
        # Setup LLM mock
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = ProposalOutput(
            search_query="weather Paris",
            proposed_action="Search for current weather in Paris.",
        )

        mock_tool = MagicMock()
        mock_get_tool.return_value = mock_tool

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()

        # Phase 1: Generate proposal
        state, thread_id = service.generate_proposal("What's the weather in Paris?")

        assert state["search_query"] == "weather Paris"

        # Phase 2: Reject
        result = service.resume_with_decision(
            thread_id=thread_id,
            decision={
                "approved": False,
                "edited_query": "weather Paris",
                "feedback": "I already know this.",
            },
        )

        assert result["approved"] is False
        assert result["human_feedback"] == "I already know this."
        # Tavily should NOT have been called
        mock_tool.invoke.assert_not_called()


class TestEditedQueryFlow:
    """
    Test the flow where human edits the query before approving.
    """

    @patch("hitl_search_agent.graph.nodes._get_web_search_tool")
    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_edited_query_is_used(self, mock_get_llm, mock_get_tool):
        """The edited query should be passed to Tavily, not the original."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = ProposalOutput(
            search_query="original query",
            proposed_action="Search for original.",
        )

        mock_summary = MagicMock()
        mock_summary.content = "Summary."
        mock_llm.invoke.return_value = mock_summary

        mock_tool = MagicMock()
        mock_get_tool.return_value = mock_tool
        mock_tool.invoke.return_value = {"images": [], "results": []}

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()

        _, thread_id = service.generate_proposal("test")

        result = service.resume_with_decision(
            thread_id=thread_id,
            decision={
                "approved": True,
                "edited_query": "edited and improved query",
                "feedback": "",
            },
        )

        assert result["search_query"] == "edited and improved query"

        # Verify Tavily received the edited query
        tavily_call = mock_tool.invoke.call_args[0][0]
        assert tavily_call["query"] == "edited and improved query"
