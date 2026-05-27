"""
Tests for hitl_search_agent.graph.nodes

These tests mock the LLM and web search tool to verify node logic
without making real API calls.
"""

from unittest.mock import patch, MagicMock

from hitl_search_agent.domain.state import make_initial_state
from hitl_search_agent.domain.models import ProposalOutput


class TestProposeActionNode:
    """Tests for the propose_action graph node."""

    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_propose_action_returns_structured_output(self, mock_get_llm):
        """The node should use structured output and populate state fields."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        # with_structured_output returns a new chain-like object
        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = ProposalOutput(
            search_query="LangGraph HITL features 2025",
            proposed_action="Search for LangGraph human-in-the-loop features.",
        )

        from hitl_search_agent.graph.nodes import propose_action

        state = make_initial_state("Show me LangGraph HITL features")
        result = propose_action(state)

        assert result["search_query"] == "LangGraph HITL features 2025"
        assert "LangGraph" in result["proposed_action"]
        assert len(result["messages"]) == 1

        # Verify structured output was used
        mock_llm.with_structured_output.assert_called_once_with(ProposalOutput)

    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_propose_action_calls_llm_with_system_prompt(self, mock_get_llm):
        """Verify the system prompt is passed to the LLM."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_structured = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = ProposalOutput(
            search_query="test query",
            proposed_action="test action",
        )

        from hitl_search_agent.graph.nodes import propose_action

        state = make_initial_state("test request")
        propose_action(state)

        call_args = mock_structured.invoke.call_args[0][0]
        # First message should be SystemMessage
        assert call_args[0].content  # system prompt is non-empty
        # Second message should be HumanMessage with user request
        assert call_args[1].content == "test request"


class TestExecuteWebSearchNode:
    """Tests for the execute_web_search graph node."""

    @patch("hitl_search_agent.graph.nodes._get_web_search_tool")
    def test_execute_web_search_extracts_images(self, mock_get_tool):
        """The node should extract image URLs from Tavily results."""
        mock_tool = MagicMock()
        mock_get_tool.return_value = mock_tool
        mock_tool.invoke.return_value = {
            "images": ["http://img1.png", "http://img2.png"],
            "results": [],
        }

        from hitl_search_agent.graph.nodes import execute_web_search

        state = make_initial_state("test query")
        state["search_query"] = "test query"

        result = execute_web_search(state)

        assert result["image_urls"] == ["http://img1.png", "http://img2.png"]
        assert result["search_results"] is not None

    @patch("hitl_search_agent.graph.nodes._get_web_search_tool")
    def test_execute_web_search_retries_on_failure(self, mock_get_tool):
        """The node should retry on transient failures."""
        mock_tool = MagicMock()
        mock_get_tool.return_value = mock_tool

        # Fail twice, succeed on third attempt
        mock_tool.invoke.side_effect = [
            ConnectionError("timeout"),
            ConnectionError("timeout"),
            {"images": ["http://img.png"], "results": []},
        ]

        from hitl_search_agent.graph.nodes import execute_web_search

        state = make_initial_state("test")
        state["search_query"] = "test"

        result = execute_web_search(state)

        assert result["image_urls"] == ["http://img.png"]
        assert mock_tool.invoke.call_count == 3


class TestSummarizeSearchResultsNode:
    """Tests for the summarize_search_results graph node."""

    @patch("hitl_search_agent.graph.nodes._get_llm")
    def test_summarize_returns_result(self, mock_get_llm):
        """The node should produce a result string from the LLM."""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.content = "Here is the summary of search results."
        mock_llm.invoke.return_value = mock_response

        from hitl_search_agent.graph.nodes import summarize_search_results

        state = make_initial_state("test")
        state["search_query"] = "test query"
        state["search_results"] = {"results": []}
        state["image_urls"] = []

        result = summarize_search_results(state)

        assert result["result"] == "Here is the summary of search results."
        assert len(result["messages"]) == 1


class TestRouteAfterReview:
    """Tests for the conditional routing function."""

    def test_approved_routes_to_search(self):
        from hitl_search_agent.graph.nodes import route_after_review

        state = make_initial_state("test")
        state["approved"] = True

        assert route_after_review(state) == "execute_web_search"

    def test_rejected_routes_to_end(self):
        from langgraph.graph import END
        from hitl_search_agent.graph.nodes import route_after_review

        state = make_initial_state("test")
        state["approved"] = False

        assert route_after_review(state) == END

    def test_none_routes_to_end(self):
        from langgraph.graph import END
        from hitl_search_agent.graph.nodes import route_after_review

        state = make_initial_state("test")
        state["approved"] = None

        assert route_after_review(state) == END
