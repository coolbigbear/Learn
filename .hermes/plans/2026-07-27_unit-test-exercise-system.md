# Unit-Test Exercise System Implementation Plan

> **For Hermes:** Implement this plan phase-by-phase using kanban orchestrator with multi-agent profiles.

**Goal:** Replace the current output-based exercise testing model with a proper unit-test-style system where users implement functions/classes and the platform runs a separate test suite against them — like HackerRank or LeetCode.

**The Problem:** Currently every exercise runs the user's entire script and compares stdout against expected output. This forces students to `print()` specific strings, mixes implementation with test scaffolding, and prevents proper function-level testing with multiple arguments. The capstone project is the worst example — "exercises" just simulate concepts rather than building real components.

**The Solution:** Add a `test_suite` field to exercise definitions — Python code containing `test_*` functions that import the user's implementation and run assertions. The existing Docker/subprocess sandbox executes the test suite against the user's code, collecting per-test pass/fail results. The frontend already supports per-test result display (ExerciseFeedback component), so the UX is largely ready.

---

## Architecture Changes

### New Exercise JSON Format

Each exercise gets an optional `test_suite` field alongside the existing `test_cases`:

```json
{
  "slug": "func-add",
  "title": "Addition function",
  "instruction": "Define a function `add(a, b)` that **returns** the sum of a and b.",
  "starter_code": "def add(a, b):\n    # Return the sum of a and b\n    pass",
  "test_suite": "def test_adds_two_positive():\n    result = add(7, 12)\n    assert result == 19, f\"Expected 19, got {result}\"\n\ndef test_adds_zero():\n    result = add(0, 5)\n    assert result == 5, f\"Expected 5, got {result}\"\n\ndef test_adds_negative():\n    result = add(-3, 10)\n    assert result == 7, f\"Expected 7, got {result}\"\n\ndef test_both_negative():\n    result = add(-5, -7)\n    assert result == -12, f\"Expected -12, got {result}\"",
  "solution_code": "def add(a, b):\n    return a + b",
  "test_cases": []
}
```

**Rules:**
- `test_suite` contains Python code only — no markdown, no JSON
- Functions named `test_*` are auto-discovered and run as individual tests
- Each `test_*` function uses plain `assert` statements
- Assertion messages are user-facing failure messages
- If `test_suite` is absent/null, the harness falls back to the current `test_cases` output-comparison model (backward compatible)

### Harness Changes (exercise_runner.py + docker_runner.py)

**New execution mode — `test_suite` present:**

```
1. Write user code to exercise.py
2. Write test suite to test_suite.py
3. Execute: python3 -c "
     import sys, types, json
     # Import user code as a module
     import importlib.util
     spec = importlib.util.spec_from_file_location('exercise', 'exercise.py')
     module = importlib.util.module_from_spec(spec)
     spec.loader.exec_module(module)
     
     # Execute test suite in a namespace that can access the module
     test_ns = {'exercise': module}
     exec(open('test_suite.py').read(), test_ns)
     
     # Discover and run all test_* functions
     results = []
     all_passed = True
     for name, fn in sorted(test_ns.items()):
         if name.startswith('test_') and callable(fn):
             try:
                 fn()
                 results.append({'name': name, 'passed': True, 'message': None, 'test_index': len(results)})
             except AssertionError as e:
                 all_passed = False
                 results.append({'name': name, 'passed': False, 'message': str(e) or 'Assertion failed', 'test_index': len(results)})
             except Exception as e:
                 all_passed = False
                 results.append({'name': name, 'passed': False, 'message': f'{type(e).__name__}: {e}', 'test_index': len(results)})
     
     print(json.dumps({'passed': all_passed, 'actual_output': '', 'expected_output': '', 'errors': None, 'test_results': results}))
   "
```

**Fallback mode — `test_suite` absent/null:** Use existing `test_cases` output-comparison (current behavior).

### Database Changes

**Exercise model** (`api/app/models/exercise.py`):
- Add `test_suite = Column(Text, nullable=True, default=None)` column

### Seed/Sync Changes

**content_seed.py**:
- Read `test_suite` from exercise JSON (if present)
- Sync it to the database like test_cases
- When either `test_suite` or `test_cases` changes in source, update DB

### API Schema Changes

**ExerciseDetail** (`api/app/schemas/exercise.py`):
- Add `test_suite: str | None = None`
- Keep `test_cases` on the model but don't expose via API (it was never exposed to the frontend — the frontend only gets starter_code, instruction, etc.)

**RunResult / TestResult**: No schema changes needed — they already support per-test results with `name`, `passed`, `message`, `comparison_type`.

### Frontend Changes

The `ExerciseFeedback` component already handles per-test results beautifully:
- Shows each test with name + pass/fail icon
- Shows failure messages
- Shows expected vs got for output-based tests

**Minor changes needed:**
- For test_suite results, the `comparison_type` field won't be used (was needed for output-based). The display should default to showing the assertion message
- The "Output Comparison" section at the bottom of ExerciseFeedback should be hidden when running in test_suite mode (no expected_output/actual_output to compare)
- The OutputPanel (showing stdout) should still show any print output from the user's code during execution

---

## Implementation Phases

### Phase 1: Backend — Add test_suite support (architect + backend)

| Task | Files | Description |
|------|-------|-------------|
| 1.1 Update exercise model | `api/app/models/exercise.py` | Add `test_suite` column |
| 1.2 Update API schemas | `api/app/schemas/exercise.py` | Add `test_suite` to ExerciseDetail |
| 1.3 Update content seed/sync | `api/app/services/content_seed.py` | Read and sync `test_suite` from JSON |
| 1.4 New harness mode (subprocess) | `api/app/services/exercise_runner.py` | Add `_build_test_suite_runner()` function — new execution mode for test_suite |
| 1.5 New harness mode (Docker) | `api/docker/harnesses/python_harness.py.j2` | Add test_suite execution mode to Docker harness template |
| 1.6 Wire up router | `api/app/routers/exercises.py` | Router already passes `exercise.test_cases` — add logic to use `exercise.test_suite` when present |
| 1.7 Migration script | `scripts/migrate_exercises.py` | Script to read existing JSON exercises, add empty `test_suite` field for backward compat |

**Verification:** Submit a test exercise with test_suite via API, verify per-test results come back.

### Phase 2: Frontend — Adapt display for test_suite mode (architect + frontend)

| Task | Files | Description |
|------|-------|-------------|
| 2.1 Update ExerciseFeedback | `frontend/src/components/ExerciseFeedback.jsx` | Hide output comparison section when running in test_suite mode; show assertion messages cleanly |
| 2.2 Add test count display | `frontend/src/components/ExerciseFeedback.jsx` | Show "X/Y tests passed" summary |
| 2.3 Update LessonView | `frontend/src/pages/LessonView.jsx` | Handle run/submit results with test_suite format |

**Verification:** Submit a passing and failing exercise via test_suite mode, verify the feedback display shows per-test results with names.

### Phase 3: Content Migration — Rewrite exercises (architect + content)

| Task | Files | Description |
|------|-------|-------------|
| 3.1 Exercise spec document | `docs/exercise-test-suite-guide.md` | Write spec for content team: test_suite format, conventions, examples |
| 3.2 Migrate lessons 1-8 (basics) | `content/python/0*/*.json` | Rewrite: numbers, strings, variables, booleans, lists, dicts, functions |
| 3.3 Migrate lessons 9-15 (intermediate) | `content/python/1*/*.json` | Rewrite: file IO, error handling, OOP, modules |
| 3.4 Migrate lessons 16-20 (data + API) | `content/python/1*/*.json` | Rewrite: CSV, JSON, data libs, HTTP |
| 3.5 Migrate lessons 21-25 (FastAPI + DB) | `content/python/2*/*.json` | Rewrite: FastAPI intro, mini project, databases |
| 3.6 Migrate lessons 26-29 (ML) | `content/python/2*/*.json` | Rewrite: numpy, preprocessing, supervised, unsupervised |
| 3.7 Migrate lessons 30-32 (API advanced) | `content/python/3*/*.json` | Rewrite: auth, XML, capstone — real component building |
| 3.8 Update manifest.json | `content/python/manifest.json` | Ensure any path changes are reflected |

**Verification:** After each lesson migration, run `python3 scripts/_check_content.py` to verify all exercises parse correctly.

### Phase 4: QA & Verification (architect + reviewer + user)

| Task | Description |
|------|-------------|
| 4.1 Backend QA | Review test_suite harness for correctness, sandbox escape vectors, edge cases |
| 4.2 Frontend QA | Browser test: submit passing/failing exercises, verify feedback display |
| 4.3 Content QA | Sample-test 3 lessons (1 beginner, 1 intermediate, 1 advanced) — all tests pass with solution code |
| 4.4 User testing | Run the `user` profile through 2-3 migrated lessons using 3-pass pattern (lazy → wrong → correct) |
| 4.5 Migration completeness | Verify all 32 lessons have test_suite; fallback to test_cases only where specified |

---

## Key Design Decisions

1. **`test_suite` is a Python string, not a JSON structure.** This lets content authors write natural assertions without a DSL. The cost is we must exec() the test suite, which the sandbox already handles securely.

2. **Function discovery by naming convention (`test_*`).** Matches pytest convention, familiar to developers. No decorators or registration API needed.

3. **User code is saved to `exercise.py` and imported as a module.** This is cleaner than exec() with shared namespace — the user's module gets its own `__name__`, `__file__`, etc. The test suite imports from it.

4. **Backward compatible by default.** Exercises without `test_suite` continue using the current output-comparison model. This lets us migrate content incrementally without breaking existing lessons.

5. **The harness (both Docker and subprocess) gets a new code path.** The existing output-comparison code stays untouched. This minimizes regression risk.

6. **Docker sandbox takes priority, subprocess falls back.** Same as today — no change to the deployment model.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| User code defines `test_*` functions that conflict with the test suite | Run test suite in a separate namespace; only `test_*` from the test suite file are collected |
| User code defines things that break when imported (side effects at module level) | This is already a problem with the current model (exec runs everything). The sandbox limits apply. Doc guidance: starter code should avoid top-level side effects |
| Content migration is 200+ exercises across 32 lessons | Split into sub-phases by lesson group. Phase 3.1-3.7 each take 2-4 lessons. Run in parallel via content profile |
| Test suite encourages bad testing patterns (fragile tests, testing implementation not behavior) | Include a test-suite authoring guide in the plan. Review test suites during QA |
| Existing progress data references old test_cases | Progress only stores "completed" boolean + submitted code. Changing the testing model doesn't invalidate past completions |

---

## Git Workflow

```
QA  ───►  feature/test-suite-exercise-system  ──►  PR into QA  ──►  deploy to staging
```

1. Create feature branch from QA
2. Implement Phase 1 (backend) + Phase 2 (frontend) on the feature branch
3. Commit and push → PR into QA
4. Deploy to staging (GitHub Actions auto-deploys QA branch)
5. Run Phase 4 QA against staging
6. Content migration (Phase 3) can happen on the same feature branch or a follow-up

Each phase should be a separate PR where possible for incremental review.
