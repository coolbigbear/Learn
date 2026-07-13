# Team & Task Graph — Interactive Python Tutorials

## Team

| Profile | Role | Toolsets | What they deliver |
|---|---|---|---|
| `architect` | Director/planner | kanban, terminal, file | Architecture spec, API design, task decomposition, review gates |
| `backend` | API builder | kanban, terminal, file, web | FastAPI app, exercise engine, database models, API endpoints |
| `frontend` | UI builder | kanban, terminal, file, web | React app, interactive code editor, lesson viewer, progress UI |
| `content` | Tutorial author | kanban, file | 15 Python lessons, exercises, quizzes, sample code |
| `reviewer` | QA/integration | kanban, terminal, file, browser, web | Integration tests, code review, smoke tests, QA report |
| `user` | Learner-simulator QA | kanban, browser, terminal | Exercises the app as a real beginner — 3-pass testing, bug reports, UX feedback |

## Task Graph

```
T0: root — "Build interactive Python tutorial website"
 │
 ├── T1: architect  "Design system architecture + API spec"              (parent: T0)
 │    │
 │    ├── T2: backend  "Build FastAPI skeleton + exercise engine"        (parent: T1)
 │    │    └── T4: backend  "Implement all API endpoints + auth"         (parent: T2)
 │    │
 │    ├── T3: frontend "Build React app skeleton + router + layout"      (parent: T1)
 │    │    ├── T5: frontend "Build lesson viewer + markdown renderer"    (parent: T3)
 │    │    └── T6: frontend "Build interactive code editor + runner"     (parent: T3)
 │    │
 │    └── T7: content  "Write lessons 1-8 (basics through functions)"    (parent: T1)
 │         └── T8: content  "Write lessons 9-15 (IO through API)"        (parent: T7)
 │
 ├── T9: reviewer   "Review backend + frontend integration"              (parents: T4, T5, T6)
 │
 └── T10: reviewer  "Full integration test + QA sign-off"                (parents: T8, T9)
```

## Team Culture & Autonomy

You are a **team**, not a collection of isolated workers. Act like it.

- **Talk to each other.** Use task comments to ask questions, share findings, flag concerns, hand off context, or give a heads-up. A quick comment can save another agent hours of confusion. Before asking the human anything, ask the team first — someone probably knows the answer.
- **Create tickets for each other.** If you spot work that belongs in another profile's lane, create a task for them. Don't silently work around it, don't block and wait — create the ticket, add a comment with context, and move on. The kanban board is your shared nervous system.
- **Be autonomous.** The human is busy. Exhaust every option among the team before escalating. Read the brief, read TEAM.md, read existing task comments, check the codebase — the answer is almost always already there. Only ask the human when the decision genuinely requires their judgment and no amount of team discussion can resolve it.
- **Resolve things peer-to-peer.** Backend changed the API shape? Comment on the frontend's task so they know. Frontend needs a new endpoint? Create a backend task, don't hack around it. Content has a question about the exercise format? Ask in a comment. The team self-organizes through the board.
- **No hero complex.** One agent should not silently absorb another's work. If the backend task is stalled and you're frontend, don't rewrite the API yourself — comment, create a follow-up task, keep the team loop intact. Boundaries exist so the team stays coherent, not to block progress.

The human sets the direction. The team figures out how to get there — together.

## Key Rules

1. **Shared workspace.** Every task uses workspace_kind="dir" with workspace_path="/opt/data/projects/python-tutorials" and tenant="interactive-python-tutorials".
2. **QA tickets are UNASSIGNED.** The `user` (learner-simulator QA) profile must never assign tickets to itself. When the user profile finds a bug or missing feature, it creates a ticket with `assignee: null` (no assignee) and leaves assignment to the orchestrator/dispatcher. This applies to ALL tickets involving code changes, content edits, or UI work — only QA/testing tickets ever get assigned to `user`.
3. **Dependencies.** A task's parents must be completed before it can start.
4. **Review gates.** T9 and T10 are mandatory — nothing ships without review.
5. **Heartbeats.** Long-running tasks (>5min) should emit kanban_heartbeat with progress.

## Blocking Policy

Tasks should **only** be blocked when they genuinely need human input — a decision, clarification, or approval that only a human can make. Examples of legitimate blockers:

- Ambiguous requirements that need the user to clarify
- A design trade-off the user must weigh in on
- An external dependency is unavailable and the user needs to arrange it

Code issues, bugs, failing tests, missing features, or incomplete work from another agent are **not** reasons to block a task. Instead, the agent should **create a new task** assigned to the appropriate profile to resolve the issue, and add it as a dependency.

## Git Worktree Isolation

Every code-changing task runs in its own **git worktree** — a fully isolated working directory branched from `main`. This is enforced structurally, not procedurally.

```
main (QA tests HERE)          worktree: fix-login          worktree: fix-api-500
     │                              │                            │
     ├── stable, tested             ├── isolated changes         ├── isolated changes
     ├── QA never sees WIP          ├── merged when done         ├── merged when done
     └── ONLY merged fixes land     └── never touches main       └── never touches main
```

### How It Works

1. **`main` is the source of truth.** QA always tests against `main` (or a deployed build from `main`). Nothing lands on `main` until it's reviewed and merged.
2. **Every dev task spawns with `hermes -w`.** The kanban dispatcher passes `--worktree` when spawning worker profiles. The agent gets its own worktree at `.worktrees/<task-id>/` — a full copy of the repo, isolated from every other agent.
3. **Changes never leak.** Worktree A cannot see worktree B's uncommitted changes. QA cannot see unfinished fixes. This is a git-level guarantee, not a hope that agents "follow the rules."
4. **Merge gate.** A fix task only completes by committing to its worktree, pushing the branch, and merging to `main`. Until the merge happens, `main` is untouched.
5. **QA re-tests on updated `main`.** After fixes merge, the follow-up QA task runs against the new `main` — which now includes the fixes.

### Why Worktrees

| Without worktrees | With worktrees |
|---|---|
| QA tests dev's half-finished changes → false failures | QA only sees merged, committed code |
| Two devs edit the same file → merge conflict chaos | Each dev has their own working tree |
| "Please don't touch X while I test" — hope-based | Git-enforced isolation — impossible to interfere |
| Reviewer runs out of iterations because devs keep changing things | Reviewer has a stable target; devs work in parallel |

The kanban dispatcher handles worktree creation automatically when `--worktree` is set on the task.

## QA Workflow (Reviewer → Fix → Reviewer)

The reviewer profile **does not write code**. Its sole job is to test and verify.

### The Golden Rule: Create Tasks IMMEDIATELY

**Every time you find an issue, create a fix task right then and there.** Do not collect issues and batch them at the end — that's how iterations run out and work gets lost. The moment a bug surfaces, stop, create the task, add a comment with specifics, then keep testing. Even if you run out of iterations two tests later, the tasks you already created survive.

### Full QA Cycle

```
┌──────────────────────────────────────────────────────┐
│  1. QA PASS: Test everything end-to-end              │
│     → Find issue? Create fix task IMMEDIATELY        │
│     → Keep testing until all features covered        │
│     → Complete the QA task (even with open fix tasks)│
│                                                      │
│  2. DEV FIX: Devs pick up fix tasks, resolve them    │
│     (QA is done testing — no conflict)               │
│                                                      │
│  3. RE-QA: New follow-up QA task verifies all fixes  │
│     → Depends on every fix task from step 1          │
│     → If more issues found, goto step 1              │
└──────────────────────────────────────────────────────┘
```

Step by step:

1. **Test everything.** Run through every feature, endpoint, and UI flow. Test the happy path, edge cases, error states, responsive layout, JS console — the works.
2. **Create fix tasks as you go.** Find a bug? Create a kanban task for the right profile immediately — don't wait. Add a comment with reproduction steps, screenshots, URLs, error messages.
3. **Complete the QA task** when your testing pass is done, even if there are open fix tasks. Write a summary comment listing all fix tasks created, what passed, and what needs re-testing.
4. **Create a follow-up QA task** that depends on ALL the fix tasks you created. This gates re-testing until every fix lands. Title it "QA: Re-verify fixes from [original QA task]".
5. **Devs fix in peace.** They pick up fix tasks knowing QA is done testing — no conflicts with a live QA session.
6. **Follow-up QA runs** once all fix tasks complete. Re-test every fix. If clean → approve and complete. If new issues → repeat the cycle.

### Why This Order Matters

- **QA never runs out of iterations with untracked bugs.** Tasks are created on-the-spot, not batched at the end.
- **Devs never change code while QA is testing it.** The QA pass finishes first, then devs start fixing. No mid-test surprises.

### What the Reviewer Can (and Cannot) Do

| Can do | Cannot do |
|---|---|
| Test the app end-to-end (browser, API calls) | Write or modify application code |
| Create tasks for backend/frontend to fix bugs | Fix bugs directly |
| Create tasks to update unit tests or UI tests | Write unit tests or UI tests themselves |
| Verify fixes by re-running tests | Deploy or configure infrastructure |
| Report findings and approve/reject deliverables | Make architectural decisions |

### Example

```
T9: reviewer "QA: Verify backend + frontend integration"
 │  Tests login flow — PASS
 │  Tests lesson list — finds 500 error
 │    → CREATES T9a: backend "Fix lesson list 500 error" IMMEDIATELY
 │  Tests code editor — PASS
 │  Tests progress tracking — finds broken redirect
 │    → CREATES T9b: frontend "Fix progress redirect after save" IMMEDIATELY
 │  Tests remaining features — PASS
 │  Completes T9 with summary comment
 │  CREATES T10: reviewer "QA: Re-verify fixes from T9"
 │                depends on [T9a, T9b]
 │
 T9a (backend) and T9b (frontend) run in parallel
 │
 T10: reviewer "QA: Re-verify fixes"
 │  Re-tests lesson list — PASS (T9a fixed it)
 │  Re-tests progress tracking — PASS (T9b fixed it)
 │  Full regression — PASS
 │  Completes with approval ✓
```

## Role Boundaries

Each profile stays in its lane. No profile oversteps into another's domain:

| Profile | Owns | Never does |
|---|---|---|
| `architect` | Architecture, task decomposition, review gates | Writing code, tests, or content |
| `backend` | API code, database, exercise engine | Frontend UI, lesson content, browser testing |
| `frontend` | React components, styling, client-side logic | Backend APIs, lesson content, database changes |
| `content` | Lesson markdown, exercises, quizzes | Code changes (frontend or backend) |
| `reviewer` | Testing, verification, QA reports, bug tickets | Writing or modifying any code or content |
| `user` | Testing the app as a beginner, reporting bugs and UX issues | Writing code, fixing bugs, researching solutions, writing content |