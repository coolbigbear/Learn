"""Exercise Pydantic schemas."""

from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = Field(default="python", max_length=20)


class TestResult(BaseModel):
    test_index: int
    passed: bool
    actual_output: str
    expected_output: str
    errors: str | None = None
    name: str | None = None
    message: str | None = None
    comparison_type: str = "exact"


class RunResult(BaseModel):
    passed: bool
    actual_output: str
    expected_output: str
    errors: str | None = None
    test_results: list[TestResult]


class ExerciseDetail(BaseModel):
    id: int
    slug: str
    title: str
    instruction: str
    starter_code: str
    language: str = "python"
    order: int
    lesson_id: int
    test_suite: str | None = None  # Read-only; used by exercise runner
