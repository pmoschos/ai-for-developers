"""
JobRadar — Pydantic models for typed inter-agent data flow.

Each model represents the structured output of one pipeline stage.
Teaching note: these are the "API contracts" between agents.
              Agent 1 produces JobListings → Agent 2 reads JobListings
              Agent 2 produces MarketAnalysis → Agent 3 reads MarketAnalysis
              Agent 3 produces GapAnalysis → Agent 4 reads GapAnalysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ── Stage 1 output: Job Hunter ────────────────────────────────────────────────

class JobListing(BaseModel):
    """One real job found on the internet."""

    company: str = Field(description="Company offering the role (e.g. 'Stripe')")
    title: str = Field(description="Exact job title as posted")
    location: str = Field(description="Location or 'Remote'")
    salary_range: Optional[str] = Field(
        default=None,
        description="Salary range if publicly displayed, e.g. '€60K–€80K'. Null if not shown.",
    )
    apply_url: str = Field(description="Direct URL to the job posting or application page")
    key_requirements: List[str] = Field(
        description="Full list of required skills, tools, and technologies extracted from the posting"
    )
    years_experience_required: Optional[str] = Field(
        default=None,
        description="Experience level, e.g. '2-4 years' or 'Senior (5+)'. Null if not specified.",
    )
    is_remote: bool = Field(description="True if the role is fully remote or remote-friendly")


class JobListings(BaseModel):
    """
    The complete collection of real job postings found by the Job Hunter agent.
    This is the output of Stage 1 — passed as context to Stage 2 (Market Analyst).
    """

    jobs: List[JobListing] = Field(description="List of verified job postings found")
    total_found: int = Field(description="Total number of jobs collected")
    search_query_used: str = Field(
        description="The main search query used to find these jobs (for transparency)"
    )


# ── Stage 2 output: Market Analyst ────────────────────────────────────────────

class SkillDemand(BaseModel):
    """
    How frequently a specific skill appears across all job listings.
    Teaching note: this is computed by the agent by COUNTING occurrences,
                   not by guessing. Every percentage must be traceable.
    """

    skill: str = Field(description="Skill or technology name, e.g. 'FastAPI', 'Docker', 'Python'")
    frequency_pct: float = Field(
        description="Percentage of job listings that mention this skill (0–100)"
    )
    is_critical: bool = Field(
        description="True if this skill appears in more than 50% of listings — i.e. a must-have"
    )


class MarketAnalysis(BaseModel):
    """
    What the job market actually wants, extracted from all job listings.
    This is the output of Stage 2 — passed as context to Stage 3 (Gap Advisor).

    Teaching note: notice how this model has NO free-text fields except market_summary.
                   Everything else is structured and quantified. This is intentional —
                   it forces the agent to produce concrete, measurable outputs.
    """

    most_wanted_skills: List[SkillDemand] = Field(
        description="All skills found, sorted by frequency (highest first)"
    )
    typical_tech_stack: List[str] = Field(
        description="Top 5-8 technologies that form the core stack for this role"
    )
    median_salary: Optional[str] = Field(
        default=None,
        description="Median salary across listings that show pay, e.g. '€72,000'. Null if insufficient data.",
    )
    salary_range_full: Optional[str] = Field(
        default=None,
        description="Full range from lowest to highest, e.g. '€50K–€100K'",
    )
    experience_range: str = Field(
        description="Typical experience range requested, e.g. '2–5 years'"
    )
    remote_ratio_pct: int = Field(
        description="Percentage of listings that are remote or remote-friendly (0–100)"
    )
    market_summary: str = Field(
        description="2-3 sentence plain-English summary of what the market wants for this role"
    )


# ── Stage 3 output: Gap Advisor ───────────────────────────────────────────────

class GapAnalysis(BaseModel):
    """
    Comparison between what the market wants and what the candidate has.
    This is the output of Stage 3 — used as context by Stage 4 (Roadmap Writer).

    Teaching note: the readiness_score is calculated as:
                   (# critical skills candidate HAS) / (# total critical skills) × 100
                   This makes it objective and explainable, not a gut feeling.
    """

    readiness_score: int = Field(
        description=(
            "Overall market readiness score (0–100). "
            "Formula: matched critical skills ÷ total critical skills × 100"
        )
    )
    readiness_label: str = Field(
        description="Human label for the score: 'Ready to Apply' | 'Almost Ready' | 'Needs Work' | 'Early Stage'"
    )
    skills_you_have: List[str] = Field(
        description="Skills from the candidate's CV that match market requirements"
    )
    critical_gaps: List[str] = Field(
        description=(
            "Skills appearing in >50% of job listings that are ABSENT from the candidate's CV. "
            "These are the most important to learn."
        )
    )
    nice_to_have_gaps: List[str] = Field(
        description="Skills in 20–50% of listings, absent from CV. Important but not blocking."
    )
    apply_now_jobs: List[str] = Field(
        description="Job titles from the listings the candidate qualifies for RIGHT NOW"
    )
    apply_in_3_months: List[str] = Field(
        description="Job titles to target after closing the critical gaps (90 days)"
    )
    strengths_summary: str = Field(
        description="1-2 sentences about what the candidate already does well"
    )
