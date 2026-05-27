"""
JobRadar — crew.py
Defines the 4-agent hierarchical crew using CrewAI's @CrewBase decorator pattern.

Teaching notes:
  @CrewBase   — marks this class as a CrewAI crew (enables @agent/@task/@crew decorators)
  @agent      — registers a method as an agent factory
  @task       — registers a method as a task factory
  @crew       — the method that assembles and returns the Crew object

  The `agents_config` and `tasks_config` class variables tell @CrewBase where to find
  the YAML files. Methods decorated with @agent automatically receive the matching
  YAML config via `self.agents_config["agent_name"]`.

  Process.hierarchical means a Director (manager_agent) coordinates everything.
  The Director delegates, checks quality, and can request rewrites.
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import TavilySearchTool

from .models import GapAnalysis, JobListings, MarketAnalysis
from .tools.fetch_tool import WebFetchTool
from .tools.notify_tool import NotificationTool


@CrewBase
class JobRadar:
    """
    JobRadar — Job Market Intelligence Crew

    Pipeline (executed in order):
        Job Hunter  →  Market Analyst  →  Gap Advisor  →  Roadmap Writer
        (find jobs)    (count skills)     (compare CV)    (write roadmap)

    Coordination: Hierarchical — the Director agent delegates and enforces quality.
    Memory: Enabled (long-term SQLite + short-term RAG via OpenAI embeddings).
    """

    agents_config = "config/agents.yaml"
    tasks_config  = "config/tasks.yaml"

    # ── Shared tool factory ───────────────────────────────────────────────────
    @staticmethod
    def _research_tools() -> list:
        """
        Returns the tools available to research agents.
        TavilySearchTool  — AI-powered real-time web search (replaces SerpAPI)
        WebFetchTool      — Reads the raw content of any URL
        """
        return [TavilySearchTool(), WebFetchTool()]

    # ── Agent definitions ─────────────────────────────────────────────────────
    # Teaching note: each @agent method reads its role/goal/backstory/llm
    # from agents.yaml automatically via `self.agents_config["name"]`.
    # The Python code only adds runtime parameters (tools, limits, flags).

    @agent
    def job_hunter(self) -> Agent:
        """Stage 1 — finds real job listings via web search."""
        return Agent(
            config=self.agents_config["job_hunter"],
            tools=self._research_tools(),
            verbose=True,
            max_iter=6,
            max_retry_limit=2,
        )

    @agent
    def market_analyst(self) -> Agent:
        """Stage 2 — counts skills and extracts market patterns."""
        return Agent(
            config=self.agents_config["market_analyst"],
            tools=[WebFetchTool()],  # Can fetch a URL if needed to verify data
            verbose=True,
            max_iter=6,
            max_retry_limit=2,
        )

    @agent
    def gap_advisor(self) -> Agent:
        """Stage 3 — compares market data to the candidate's CV."""
        return Agent(
            config=self.agents_config["gap_advisor"],
            verbose=True,
            max_iter=4,
            max_retry_limit=1,
        )

    @agent
    def roadmap_writer(self) -> Agent:
        """Stage 4 — writes the 90-day learning roadmap and dispatches notifications."""
        return Agent(
            config=self.agents_config["roadmap_writer"],
            tools=[WebFetchTool(), NotificationTool()],
            verbose=True,
            max_iter=5,
            max_retry_limit=1,
        )

    # Task definitions 
    # Teaching note: `output_pydantic` tells CrewAI to validate the agent's output
    # against the specified Pydantic model. If the output doesn't match the schema,
    # the agent will be asked to retry and fix its response automatically.
    # This is the "type safety" layer of the agentic pipeline.

    # Η σειρά στη λίστα = η σειρά εκτέλεσης.

    @task
    def hunt_task(self) -> Task:
        """Task 1: Find job listings → JobListings model."""
        return Task(
            config=self.tasks_config["hunt_task"],
            output_pydantic=JobListings,   # Agent MUST return valid JobListings JSON
        )

    @task
    def analyse_task(self) -> Task:
        """Task 2: Analyse listings → MarketAnalysis model."""
        return Task(
            config=self.tasks_config["analyse_task"],
            output_pydantic=MarketAnalysis,
        )

    @task
    def gap_task(self) -> Task:
        """Task 3: Compare CV to market → GapAnalysis model."""
        return Task(
            config=self.tasks_config["gap_task"],
            output_pydantic=GapAnalysis,
        )

    @task
    def roadmap_task(self) -> Task:
        """Task 4: Write 90-day roadmap → Markdown file."""
        # No output_pydantic — this task produces free-form Markdown
        return Task(config=self.tasks_config["roadmap_task"])

    # ── Crew assembly ─────────────────────────────────────────────────────────
    @crew
    def crew(self) -> Crew:
        """
        Assembles the full JobRadar crew.

        Teaching note: The Director (manager_agent) is NOT in self.agents —
        it is a separate orchestration agent that delegates to the 4 workers.
        Process.hierarchical gives the Director authority to:
          - Assign tasks to agents
          - Review outputs before accepting them
          - Ask agents to revise vague or incomplete answers
        """
        director = Agent(
            config=self.agents_config["director"],
            allow_delegation=True,
            verbose=True,
        )

        return Crew(
            agents=self.agents,          # Auto-populated by @agent decorators
            tasks=self.tasks,            # Auto-populated by @task decorators
            process=Process.hierarchical,
            manager_agent=director,
            # memory=True activates three memory tiers:
            #   Long-term  → SQLite (persists across runs)
            #   Short-term → RAG in-memory vector store
            #   Entity     → tracks named entities (companies, skills, people)
            memory=True,
            embedder={
                "provider": "openai",
                "config": {"model_name": "text-embedding-3-large"},
            },
            verbose=True,
        )
