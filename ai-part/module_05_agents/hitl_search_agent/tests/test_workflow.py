"""
Tests for hitl_search_agent.services.search_workflow_service

These tests exercise the service-level orchestration with mocked
graph applications.
"""

from unittest.mock import patch, MagicMock


class TestSearchWorkflowServiceProposal:
    """Tests for the proposal phase."""

    @patch("hitl_search_agent.services.search_workflow_service.build_app")
    def test_generate_proposal_returns_state_and_thread_id(self, mock_build_app):
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            "messages": [],
            "user_request": "test request",
            "proposed_action": "Search for test",
            "search_query": "test query",
            "approved": None,
            "human_feedback": None,
            "human_decision": None,
            "search_results": None,
            "image_urls": [],
            "result": "",
        }
        mock_build_app.return_value = mock_app

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()
        state, thread_id = service.generate_proposal("test request")

        assert state["search_query"] == "test query"
        assert thread_id  # non-empty string
        assert len(thread_id) == 36  # UUID format

        # Verify config with thread_id was passed
        call_config = mock_app.invoke.call_args[1].get("config") or mock_app.invoke.call_args[0][1]
        assert "thread_id" in call_config["configurable"]

    @patch("hitl_search_agent.services.search_workflow_service.build_app")
    def test_generate_proposal_raises_on_failure(self, mock_build_app):
        mock_app = MagicMock()
        mock_app.invoke.side_effect = RuntimeError("LLM unavailable")
        mock_build_app.return_value = mock_app

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )
        from hitl_search_agent.utils.errors import ProposalError

        service = SearchWorkflowService()

        try:
            service.generate_proposal("test")
            assert False, "Should have raised ProposalError"
        except ProposalError as e:
            assert "LLM unavailable" in str(e)


class TestSearchWorkflowServiceResume:
    """Tests for the resume phase."""

    @patch("hitl_search_agent.services.search_workflow_service.build_app")
    def test_resume_with_approval(self, mock_build_app):
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            "messages": [],
            "user_request": "test",
            "proposed_action": "Search the web for: edited query",
            "search_query": "edited query",
            "approved": True,
            "human_feedback": "Looks good",
            "human_decision": None,
            "search_results": {"results": []},
            "image_urls": ["http://img.png"],
            "result": "Summary of results.",
        }
        mock_build_app.return_value = mock_app

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()

        result = service.resume_with_decision(
            thread_id="test-thread-123",
            decision={
                "approved": True,
                "edited_query": "edited query",
                "feedback": "Looks good",
            },
        )

        assert result["approved"] is True
        assert result["search_query"] == "edited query"
        assert result["result"] == "Summary of results."
        mock_app.invoke.assert_called_once()

    @patch("hitl_search_agent.services.search_workflow_service.build_app")
    def test_resume_with_rejection(self, mock_build_app):
        mock_app = MagicMock()
        mock_app.invoke.return_value = {
            "messages": [],
            "user_request": "test",
            "proposed_action": "Search for test",
            "search_query": "test",
            "approved": False,
            "human_feedback": "Not relevant",
            "human_decision": None,
            "search_results": None,
            "image_urls": [],
            "result": "",
        }
        mock_build_app.return_value = mock_app

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )

        service = SearchWorkflowService()

        result = service.resume_with_decision(
            thread_id="test-thread-456",
            decision={
                "approved": False,
                "edited_query": "test",
                "feedback": "Not relevant",
            },
        )

        assert result["approved"] is False

    @patch("hitl_search_agent.services.search_workflow_service.build_app")
    def test_resume_raises_on_failure(self, mock_build_app):
        mock_app = MagicMock()
        mock_app.invoke.side_effect = RuntimeError("Checkpointer error")
        mock_build_app.return_value = mock_app

        from hitl_search_agent.services.search_workflow_service import (
            SearchWorkflowService,
        )
        from hitl_search_agent.utils.errors import ResumeError

        service = SearchWorkflowService()

        try:
            service.resume_with_decision(
                thread_id="bad-thread",
                decision={"approved": True, "edited_query": "test", "feedback": ""},
            )
            assert False, "Should have raised ResumeError"
        except ResumeError as e:
            assert "Checkpointer error" in str(e)
