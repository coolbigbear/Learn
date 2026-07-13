# Interactive Python Tutorials — Project Brief

## Concept
A website that teaches Python programming through interactive, browser-based tutorials. Students write and run Python code directly in their browser, progressing from "Hello World" through to building their own API with FastAPI.

## Scope
- **Target audience:** Complete beginners to intermediate programmers
- **Content:** 15 lessons covering Python basics through API creation
- **Tech stack:** FastAPI backend + React frontend
- **Key feature:** Interactive code editor with live Python execution (sandboxed)

## Deliverables
1. FastAPI backend with:
   - User auth (simple token or session-based)
   - Lesson content API
   - Python exercise execution engine (sandboxed via subprocess or docker)
   - Progress tracking API
2. React frontend with:
   - Lesson viewer with rich markdown rendering
   - Interactive code editor (Monaco or CodeMirror)
   - Exercise submission + instant feedback
   - Progress tracking
3. 15 Python tutorial lessons (content)
4. Tests for backend, frontend, and integration

## Style
- Clean, modern UI — focused on readability
- Progressive disclosure — students only see what they need
- Immediate feedback — run code and see results in real-time

## Project Workspace
`/opt/data/projects/python-tutorials/`