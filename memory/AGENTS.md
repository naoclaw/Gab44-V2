# AGENTS.md — Coding Best Practices for Gab44 V2

> **Purpose**: Every AI agent working on this codebase must read and follow these guidelines before writing, editing, or reviewing any code.

---

## 1. General Principles

- **Minimal changes first.** Change only what is needed to satisfy the task. Never rewrite working code unless explicitly asked.
- **Read before writing.** Always explore the relevant files (e.g., `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, `PRD.md`) and the affected source files before making edits.
- **Prefer existing patterns.** Match the style, naming, and structure already used in the file you are editing. Consistency beats novelty.
- **One concern per change.** Keep commits focused. A fix for a bug should not also refactor unrelated code.
- **Never break the public contract.** API routes, exported functions, and component props are public contracts — do not rename or remove them without an explicit migration plan.

---

## 2. Backend (FastAPI / Python)

### Code Style
- Follow **PEP 8**: 4-space indentation, snake_case for variables/functions, PascalCase for classes.
- Maximum line length: **100 characters**.
- Use **type hints** on all function signatures (parameters and return types).
- Use `async def` for all route handlers and database calls; never use blocking I/O inside an async function.

### FastAPI Conventions
- Define request/response shapes as **Pydantic models** — never use raw `dict` for structured data.
- Always annotate route responses with the correct `response_model` to enforce validation and generate accurate OpenAPI docs.
- Use `HTTPException` with a descriptive `detail` string for error responses.
- Protect routes that require authentication with the `get_current_user` dependency; protect admin routes with an additional admin check.
- Group routes using the `# ============== Section ==============` comment style already established in `server.py`.

### Database (MongoDB / Motor)
- Use the existing `motor` async client — never introduce a synchronous driver.
- Always `await` database calls; never block the event loop.
- Index any field that is queried frequently (see `ARCHITECTURE.md §7` for the existing index list).
- Never store plaintext passwords; use `bcrypt` via the existing `hash_password` / `verify_password` helpers.
- Validate and sanitize all user-supplied data with Pydantic before it reaches the database.

### Security
- **Never** log or expose secrets, API keys, or JWT tokens.
- Validate and sanitize every input that originates from a user request.
- Use `python-jose` / the existing JWT helpers for token creation and verification — do not roll your own crypto.
- Rate-limit or enforce tier-based message limits for all AI endpoints (already handled in `server.py`).
- Keep dependency versions pinned in `requirements.txt`; run a security audit before bumping a version.

### Testing
- Write `pytest` tests for every new endpoint in `backend/tests/`.
- Cover happy path, edge cases (missing fields, bad types), and auth failure (401/403) scenarios.
- Run the existing test suite (`pytest tests/ -v`) before opening a PR.

---

## 3. Frontend (React / Tailwind CSS)

### Code Style
- Use **functional components** and React Hooks exclusively — no class components.
- File names for pages and components: **PascalCase** (e.g., `ChartPage.jsx`).
- Utility functions: **camelCase**.
- Maximum line length: **120 characters**.
- Destructure props at the function signature level for readability.

### State & Context
- Keep global state in the existing contexts (`AuthContext`, `ThemeContext`, `ReadingModeContext`); do not create new global stores without a clear reason.
- Use `useState` and `useEffect` for local component state; reach for `useReducer` when state transitions become complex.
- Clean up subscriptions and async operations in `useEffect` cleanup functions to prevent memory leaks.

### Styling (Tailwind CSS + Shadcn UI)
- Use **Tailwind utility classes** for all styling — do not add custom CSS unless a utility class does not exist.
- Follow the **design tokens** defined in `design_guidelines.json` and `DESIGN_SYSTEM.md` for colors, spacing, and typography.
- Use the existing **Shadcn/ui** component library (`components/ui/`); do not install a second UI library.
- Apply glass-morphism effects and dark/light theme classes exactly as defined in `index.css`.
- All new pages and components must be responsive (mobile-first; test at ≥ 375 px viewport width).

### API Calls
- Use `axios` through the existing API helper patterns; always include the JWT `Authorization` header for protected routes.
- Always handle loading and error states in the UI — never leave the user looking at a blank screen.
- Display meaningful error messages via the existing **sonner** toast system.

### Security
- Never store sensitive data (tokens, PII) in `sessionStorage` or in component state beyond what is already kept in `AuthContext`.
- Sanitize any user-provided strings before rendering them as HTML to prevent XSS.
- Do not expose secret keys in frontend code or environment variables prefixed with `REACT_APP_` beyond what is strictly necessary.

### Testing
- Test new components with the existing testing infrastructure if present.
- At minimum, manually verify the component at mobile (≥ 375 px), tablet (768 px), and desktop (1280 px) breakpoints before marking a task complete.

---

## 4. Git & Workflow

- **Branch naming**: `feature/<short-description>`, `fix/<short-description>`, `chore/<short-description>`.
- **Commit messages**: imperative mood, present tense, ≤ 72 characters (e.g., `add transit filter endpoint`).
- **Never commit**: `.env` files, compiled build artifacts, `node_modules/`, `__pycache__/`, or any secret.
- Open a pull request for every change, no matter how small. Include a description of what changed and why.
- Run linting and tests locally before pushing.

---

## 5. Documentation

- Update the relevant `memory/` file when you change architecture, routes, design tokens, or brand rules.
- Add inline comments only when the *why* is non-obvious — do not comment the *what*.
- Keep docstrings on public functions/classes concise and accurate.

---

## 6. Performance

- Respect the **24-hour cache** on daily guidance and other expensive AI calls — do not bypass it.
- Use pagination for all list endpoints (chat history, admin user list, etc.).
- Lazy-load large page sections on the frontend where possible.
- Profile before optimizing — do not prematurely optimize code that is not a measured bottleneck.

---

## 7. AI / LLM Integration

- Always inject the user's full chart context into system prompts exactly as the existing `get_ai_coach_response()` pattern does.
- Never send raw database documents to the LLM — project only the fields required by the prompt.
- Handle OpenAI API errors gracefully; surface a friendly fallback message to the user rather than a raw exception.
- Log token usage in debug mode only; never log the contents of user messages in production.

---

*For architecture details see `ARCHITECTURE.md`. For design rules see `DESIGN_SYSTEM.md` and `design_guidelines.json`. For brand voice see `BRAND_IDENTITY.md`.*
