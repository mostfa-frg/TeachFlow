# Development and configuration

Install the single dependency set from the repository root with `python -m pip install -r requirements.txt`, copy `.env.example` to the repository-root `.env`, then follow the root README to migrate and start the API. Keep the root `pytest.ini` as the single test configuration. Tests use an isolated in-memory SQLite database and a mocked generator; they need neither PostgreSQL nor paid provider access.

## Environment

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database connection | `sqlite:///./data/teachflow.db` |
| `TEACHFLOW_DATA_DIR` | Local original-file and extracted-text storage root | `./data` |
| `MAX_UPLOAD_BYTES` | Maximum upload size | `10485760` |
| `LLM_API_KEY` | Secret for the configured OpenAI-compatible endpoint (Groq API key) | unset |
| `LLM_BASE_URL` | Provider API base URL | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | Provider model identifier | `openai/gpt-oss-20b` |
| `LLM_API_STYLE` | API format: `responses` or `chat_completions` | `chat_completions` |
| `LLM_TIMEOUT_SECONDS` | Provider request timeout | `60` |

The API starts without LLM credentials. Roadmap generation then returns HTTP 503. For Groq, set `LLM_API_KEY` to a key from GroqCloud and use the configured Groq base URL, `openai/gpt-oss-20b` model, and `chat_completions` API style. Groq applies account and model-specific rate limits; check your GroqCloud limits if requests are rejected. Other OpenAI-compatible providers can be used by setting their matching base URL, model ID, and supported API style. Use a PostgreSQL SQLAlchemy URL for deployment and install a driver such as `psycopg[binary]` separately; SQLite remains useful for a single-process local setup.

## API outline

- `GET /health`, `GET /health/ready`
- `POST/GET /api/v1/courses`, `GET /api/v1/courses/{course_id}`
- `POST/GET/PUT /api/v1/courses/{course_id}/groups`
- `POST/GET/DELETE /api/v1/courses/{course_id}/materials`
- `POST /api/v1/courses/{course_id}/roadmaps/generate`
- `GET/PUT /api/v1/roadmaps/{roadmap_id}`, `POST /api/v1/roadmaps/{roadmap_id}/approve`
- `PUT /api/v1/groups/{group_id}/sessions/{session_id}/progress`, `GET /api/v1/groups/{group_id}/progress`

HTTP and request-validation errors use an `error` response envelope. Uploaded formats currently supported for extraction are `.txt`, `.md`, and text-based `.pdf`; OCR, DOCX, PPTX, and notebooks are unsupported. Extraction is synchronous with the upload request. Large or scanned files should not be described as analyzed.

## Current limitations / next work

Authentication, instructor scoping, complete progress controls in the interface, richer PDF resource limits, background ingestion, OCR, provider-specific evaluation, and calendar connections remain incomplete. Implement authentication before exposing this beyond local development.
