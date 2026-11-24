"""Optional Chromium acceptance checks against the explicitly labelled replay server."""

import os
import shutil
from io import BytesIO
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from pypdf import PdfWriter

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def verify(url, course):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=os.environ.get("TEACHFLOW_CHROMIUM")
            or shutil.which("chromium")
        )
        page = browser.new_page(viewport={"width": 1440, "height": 920})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_default_timeout(7000)
        action = lambda name: page.locator(f'[data-action="{name}"]').first
        page.goto(url)
        expect(page.locator("#fixture-mode")).to_be_visible()
        expect(page.locator("#course-select")).to_have_value(course)
        choose_group = page.get_by_role("button", name="Select group")
        choose_group.click()
        page.get_by_role("option", name="Saturday group").click()
        expect(page.get_by_role("button", name="Open Functions")).to_have_count(0)
        choose_group.click()
        page.get_by_role("option", name="Monday group").click()
        page.get_by_role("button", name="Open Functions").first.click()
        expect(page.locator("#session-detail-panel")).to_contain_text("Explain function arguments")
        page.route(
            "**/api/v1/courses",
            lambda route: route.fulfill(status=503, json={"error": {"message": "Local retry check"}}),
            times=1,
        )
        action("materials").click()
        expect(page.get_by_role("alert")).to_contain_text("Local retry check")
        page.get_by_role("button", name="Retry", exact=True).click()
        expect(page.get_by_role("heading", name="functions.md")).to_be_visible()
        expect(page.get_by_text("Functions, lines", exact=False).first).to_be_visible()
        action("roadmap").click()
        action("roadmap-list").click()
        page.get_by_role("button", name="1. Functions").press("Enter")
        expect(page.locator("#session-detail-panel")).to_contain_text(
            "Explain function arguments"
        )
        action("roadmap-progress").click()
        expect(page.get_by_role("heading", name="Group benchmarks")).to_be_visible()
        loops = page.locator("article", has=page.get_by_role("heading", name="Loops", exact=True))
        loops.get_by_label("Target date").fill("2020-01-02")
        with page.expect_response(lambda response: response.url.endswith("/benchmark")) as saved:
            loops.get_by_role("button", name="Save target").click()
        assert saved.value.ok and saved.value.json()["target_date"] == "2020-01-02", saved.value.text()
        expect(loops).to_contain_text("behind")
        page.reload()
        expect(page.locator("#course-select")).to_have_value(course)
        action("roadmap").click()
        action("roadmap-progress").click()
        expect(loops.get_by_label("Target date")).to_have_value("2020-01-02")
        action("approvals").click()
        expect(page.get_by_role("heading", name="Approval history")).to_be_visible()
        expect(page.get_by_text("No records to show.")).to_be_visible()
        action("assistant").click()
        field = page.get_by_label("Question", exact=True)
        field.fill("What is a loop?")
        # One local transport failure checks that retry preserves the question.
        page.route(
            "**/assistant",
            lambda route: route.fulfill(
                status=503, json={"error": {"message": "Demo retry"}}
            ),
            times=1,
        )
        page.get_by_role("button", name="Ask", exact=True).click()
        expect(
            page.get_by_text("Demo retry. Press Ask to retry.", exact=False).or_(
                page.get_by_text("Demo retry Press Ask to retry.", exact=False)
            )
        ).to_be_visible()
        page.get_by_role("button", name="Ask", exact=True).click()
        expect(page.locator('[role="log"]')).to_contain_text("loops.txt")
        action("roadmap").click()
        page.locator("[data-action=select-node][data-id=functions]").click()
        action("open-session-review").click()
        page.locator("#transcript-file").set_input_files(
            str(EXAMPLES / "transcript.txt")
        )
        page.locator("#upload-transcript").click()
        expect(page.locator("blockquote")).to_contain_text(
            "A function accepts arguments"
        )
        # Navigate from the pending queue to an existing review and package.
        action("approvals").click()
        pending_review = page.locator('[data-action="review-pending"][data-kind="review"]')
        expect(pending_review).to_have_text("Review Transcript: transcript.txt")
        expect(page.locator(".nav-count")).to_have_text("1")
        pending_review.click()
        expect(page.locator("blockquote")).to_contain_text("A function accepts arguments")
        page.locator("#approve-review").click()
        page.locator("#package").click()
        expect(page.locator("[data-item=summary]")).to_be_visible()
        action("approvals").click()
        page.locator('[data-action="review-pending"][data-kind="package"]').click()
        for key in ("summary", "recap", "homework", "group_message"):
            section = page.locator(f'[data-item="{key}"]')
            section.locator("textarea").fill("Edited demo " + key)
            section.get_by_role("button", name="Approve item").click()
            expect(section.get_by_role("button", name="Copy")).to_be_visible()
        action("approvals").click()
        expect(page.locator(".nav-count")).to_have_text("0")
        expect(page.locator('[data-action="review-pending"]')).to_have_count(0)
        page.reload()
        expect(page.locator("#course-select")).to_have_value(course)
        action("roadmap").click()
        page.locator('[data-action="select-node"][data-id="loops"]').click()
        expect(page.locator("#session-detail-panel")).to_contain_text("loops.txt")
        expect(page.locator("#session-detail-panel")).to_contain_text("Chars 0")
        action("edit-roadmap").click()
        page.locator('[data-action="select-node"][data-id="loops"]').click()
        expect(page.locator("#topic-memberships option:checked")).to_have_count(2)
        expect(page.locator("#session-citations option:checked")).to_contain_text("loops.txt")
        action("save-draft").click()
        action("approvals").click()
        page.locator('[data-action="review-pending"][data-kind="roadmap"]').click()
        expect(page.locator("#edit-title")).to_be_visible()
        action("approve").click()
        expect(action("edit-roadmap")).to_be_visible()
        action("new-course").click()
        page.locator("#name").fill("Browser setup")
        action("continue").click()
        page.locator("#calendar-file").set_input_files(
            str(EXAMPLES / "schedules/monday.csv")
        )
        expect(action("confirm-calendar")).to_be_enabled()
        page.locator("[data-gfield=name]").last.fill("Edited Monday")
        action("confirm-calendar").click()
        action("add-group").click()
        page.locator("[data-gfield=name]").last.fill("Manual group")
        action("continue").click()
        page.locator("#file-input").set_input_files(
            {
                "name": "slides.pptx",
                "mimeType": "application/octet-stream",
                "buffer": b"synthetic unsupported file",
            }
        )
        expect(page.locator(".toast").last).to_contain_text("Export DOCX or PPTX")
        expect(page.locator(".file-info")).to_have_count(0)
        pdf = PdfWriter()
        pdf.add_blank_page(width=72, height=72)
        blank_page = BytesIO()
        pdf.write(blank_page)
        page.locator("#file-input").set_input_files({
            "name": "no-text.pdf", "mimeType": "application/pdf", "buffer": blank_page.getvalue()
        })
        expect(page.locator(".file-info", has_text="no-text.pdf")).to_contain_text("supply a text export")
        page.locator("#file-input").set_input_files(
            str(EXAMPLES / "materials/loops.txt")
        )
        expect(page.locator(".file-info", has_text="loops.txt")).to_contain_text("processed")
        generated = []
        page.on(
            "request",
            lambda req: (
                generated.append(req.headers.get("idempotency-key"))
                if req.url.endswith("/generate")
                else None
            ),
        )
        action("continue").click()
        page.locator("#edit-title").wait_for()
        page.get_by_role("button", name="Back to edit").click()
        action("continue").click()
        expect(page.locator("#edit-title")).to_be_visible()
        assert len(generated) == 2 and generated[0] and generated[0] != generated[1], (
            generated
        )
        page.locator("[data-action=select-node][data-id=practice]").click()
        page.locator("#edit-title").fill("Unsaved session title")
        action("delete-topic").click()
        expect(page.locator(".toast").first).to_be_visible()
        expect(page.locator("#edit-title")).to_have_value("Unsaved session title")
        expect(page.locator(".toast")).to_have_count(0, timeout=5500)
        expect(page.locator("#edit-title")).to_have_value("Unsaved session title")
        action("approve").click()
        expect(action("edit-roadmap")).to_be_visible()
        page.set_viewport_size({"width": 390, "height": 844})
        action("roadmap-list").click()
        expect(
            page.get_by_role("button", name="3. Unsaved session title")
        ).to_be_visible()
        assert not errors, errors
        browser.close()
        print(
            "PASS · Chromium setup, regeneration, toast typing, keyboard list, mobile list, reviews, approvals, assistant retry and citations"
        )
