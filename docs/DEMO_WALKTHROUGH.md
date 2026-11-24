# TeachFlow localhost demonstration

A synthetic Python course has two groups, three materials, three sessions, three directed links and a short transcript. The **recorded fixture** server displays a banner and uses the JSON files under `examples/responses/`. The normal application entry point uses its configured provider or the documented unavailable/manual behavior.

## Start on Windows

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/demo_walkthrough.py --serve
```

Open [TeachFlow on localhost](http://127.0.0.1:8000). The command runs the HTTP acceptance sequence before leaving the verified course open. Ctrl+C stops it. Each launch uses a fresh temporary database and synthetic material directory.

To rehearse setup from a blank dashboard, start the runner in empty mode.

```powershell
python scripts/demo_walkthrough.py --empty --serve
```

To exercise the normal app with persistent local SQLite, stop the fixture instance, leave the provider key unset and use:

```powershell
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Repeat the checks

```powershell
python -m pytest -q
node --test frontend/tests/roadmap-layout.test.cjs frontend/tests/session-graph.test.cjs frontend/tests/workspace.test.cjs
python scripts/demo_walkthrough.py
```

For the optional Chromium checks:

```powershell
python -m pip install playwright
python -m playwright install chromium
python scripts/demo_walkthrough.py --browser --port 0
$env:PYTHONPATH = "backend"
python backend/tests/graph_browser.py
```

The browser tests accept an existing Chromium executable via `TEACHFLOW_CHROMIUM`. Port 0 selects a free localhost port for automated verification. Every check raises an error on a failed expectation.

## Manual browser checklist

| Step | Action | Expected result |
| --- | --- | --- |
| 1. Empty dashboard | Start the empty fixture. Create Python Development. Try continuing with a blank course name first. | The form identifies the missing name. A valid name advances to groups. |
| 2. Schedule | Import `examples/schedules/saturday.ics` and `monday.csv` separately. Edit a time before confirming. Try an invalid weekday in a copy of the CSV. | Groups appear in the preview, then in setup after confirmation. Invalid rows identify the row and reason. Add a group manually or choose a corrected file to retry. |
| 3. Materials | Upload the three files from `examples/materials/`. Try an empty TXT or unsupported DOCX/PPTX, then a valid file. | Each accepted file has a status and source locations. Office files prompt for a text or text-based PDF export. A scanned PDF without extractable text asks for a text export. |
| 4. Generate and review | Continue to generation. Open session details. Inspect objectives, related topics and supporting passages. Remove one link and add it back with a different type or note. | The proposal stays editable. Regenerating after going back creates a new version. Retrying a failed request reuses its key. With the normal app and no key, generation returns 503 and offers retry. |
| 5. Approve and reload | Approve. Refresh, reopen Roadmaps and compare the related sessions in the detail panel. Open List using the keyboard. | All three links retain endpoints, direction, type and note. Reopen the Loops editor to see both topic memberships and its selected passage. The list opens the same session detail as the graph. |
| 6. Group progress | Complete Functions for Saturday only. Switch to Monday. Open Progress, change a target date, open Dashboard and select a prerequisite reminder. | Each group keeps independent goals and targets. Monday names Functions as missing and opens its details. Refresh restores saved progress. |
| 7. Review | From Functions in either group, select Review transcript & follow-up. Upload `examples/transcript.txt`. Inspect a cited passage, edit a finding and approve. Try an incorrect range first. | Evidence shows its text and offsets. An invalid excerpt cannot be saved. Empty evidence reads “No evidence found.” A package becomes available after approval. |
| 8. Follow up | Open the package, edit the recap and approve each of summary, recap, homework and group message individually. Copy an approved item. | Draft items remain editable. Open the pending package from Approvals. Its count clears after the fourth approval. History shows timestamped changes. |
| 9. Ask | Ask “What is a loop?” in Instructor Assistant. Try an unrelated question. Switch groups and inspect references for another query. | The supplied example answer cites loops.txt and its character range. Missing evidence yields a plain explanation. The normal app without credentials shows retrieved references and “AI answer unavailable.” |
| 10. Recovery and mobile | Force a request failure, restore the local connection and retry. Use the list at a narrow viewport. While a toast is visible in the review editor, continue typing. | The UI shows the error and a recovery action. Session navigation works by keyboard. Toast expiry preserves the edited field. |

## Verified on 24 November 2026

The backend suite passed 54 tests and the frontend suite passed 20. The full HTTP and Chromium walkthrough passed on Linux at port 8000. A separate graph test edited one of three session links in Chromium, approved it, refreshed the browser and checked all three directed links and their types against a fresh API response.

The browser switched between Saturday and Monday, opened a missing prerequisite by name, saved a benchmark and checked it after refresh. It opened each kind of pending proposal from Approvals, approved the four package items and verified the count reached zero. It checked the selected secondary topic, filename and passage locator in an editable roadmap, Office export guidance, a textless PDF warning and recovery from a failed Materials request. It also exercised CSV import, direct group entry, regenerated drafts, toast expiry while typing, keyboard selection, a 390-pixel session list and retrying an Assistant request. The HTTP run covered ICS import, persisted progress for two groups, evidence ranges and local approval history.

The normal app also started on port 8000 with an empty credential. It served the instructor UI, returned 503 on roadmap generation and returned retrieved references alongside “AI answer unavailable.”

The Windows commands are provided for the instructor machine. Windows execution, assistive-technology testing and live-provider output quality remain unverified. Only synthetic inputs and recorded responses were used. Copy-to-clipboard is available for manual browser verification. [Detailed results](TEST_REPORT.md)
