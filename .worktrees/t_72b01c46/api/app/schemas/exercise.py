"""Exercise Pydantic schemas."""

from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    code: str = Field(..., min_length=1)


class TestResult(BaseModel):
    test_index: int
    passed: bool
    actual_output: str
    expected_output: str
    errors: str | None = None


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
    order: int
    lesson_id: int
