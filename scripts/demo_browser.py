"""Optional Chromium acceptance checks against the explicitly labelled replay server."""
import os
from pathlib import Path
import shutil
from playwright.sync_api import expect, sync_playwright

EXAMPLES=Path(__file__).resolve().parents[1]/"examples"


def verify(url,course):
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get("TEACHFLOW_CHROMIUM") or shutil.which("chromium"))
        page=browser.new_page(viewport={"width":1440,"height":920})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_default_timeout(7000)
        action=lambda name:page.locator(f'[data-action="{name}"]').first
        page.goto(url)
        expect(page.locator('#fixture-mode')).to_be_visible()
        expect(page.locator('#course-select')).to_have_value(course)
        action("materials").click()
        expect(page.get_by_role("heading",name="functions.md")).to_be_visible()
        expect(page.get_by_text("Functions, lines",exact=False).first).to_be_visible()
        action("roadmap").click()
        action("roadmap-list").click()
        page.get_by_role("button",name="1. Functions").press("Enter")
        expect(page.locator('#session-detail-panel')).to_contain_text("Explain function arguments")
        action("roadmap-progress").click()
        expect(page.get_by_role("heading",name="Group benchmarks")).to_be_visible()
        action("approvals").click()
        expect(page.get_by_role("heading",name="Approval history")).to_be_visible()
        expect(page.get_by_text("No records to show.")).to_be_visible()
        action("assistant").click()
        field=page.get_by_label("Question",exact=True)
        field.fill("What is a loop?")
        # One local transport failure checks that retry preserves the question.
        page.route("**/assistant",lambda route: route.fulfill(status=503,json={"error":{"message":"Demo retry"}}),times=1)
        page.get_by_role("button",name="Ask",exact=True).click()
        expect(page.get_by_text("Demo retry. Press Ask to retry.",exact=False).or_(page.get_by_text("Demo retry Press Ask to retry.",exact=False))).to_be_visible()
        page.get_by_role("button",name="Ask",exact=True).click()
        expect(page.locator('[role="log"]')).to_contain_text("loops.txt")
        action("roadmap").click()
        page.locator('[data-action=select-node][data-id=functions]').click()
        action("open-session-review").click()
        page.locator('#transcript-file').set_input_files(str(EXAMPLES/"transcript.txt"))
        page.locator('#upload-transcript').click()
        expect(page.locator('blockquote')).to_contain_text("A function accepts arguments")
        page.locator('#approve-review').click()
        page.locator('#package').click()
        for key in ("summary","recap","homework","group_message"):
            section=page.locator(f'[data-item="{key}"]')
            section.locator("textarea").fill("Edited demo "+key)
            section.get_by_role("button",name="Approve item").click()
            expect(section.get_by_role("button",name="Copy")).to_be_visible()
        page.reload()
        expect(page.locator('#course-select')).to_have_value(course)
        action("new-course").click()
        page.locator('#name').fill('Browser setup')
        action("continue").click()
        page.locator('#calendar-file').set_input_files(str(EXAMPLES/"schedules/monday.csv"))
        expect(action("confirm-calendar")).to_be_enabled()
        page.locator('[data-gfield=name]').last.fill('Edited Monday')
        action("confirm-calendar").click()
        action("add-group").click()
        page.locator('[data-gfield=name]').last.fill('Manual group')
        action("continue").click()
        page.locator('#file-input').set_input_files(str(EXAMPLES/"materials/loops.txt"))
        expect(page.locator('.file-info')).to_contain_text('processed')
        generated=[]
        page.on("request",lambda req: generated.append(req.headers.get("idempotency-key")) if req.url.endswith("/generate") else None)
        action("continue").click()
        page.locator('#edit-title').wait_for()
        page.get_by_role('button',name="Back to edit").click()
        action("continue").click()
        expect(page.locator('#edit-title')).to_be_visible()
        assert len(generated)==2 and generated[0] and generated[0]!=generated[1],generated
        page.locator('[data-action=select-node][data-id=practice]').click()
        page.locator('#edit-title').fill("Unsaved session title")
        action("delete-topic").click()
        expect(page.locator('.toast').first).to_be_visible()
        expect(page.locator('#edit-title')).to_have_value("Unsaved session title")
        expect(page.locator('.toast')).to_have_count(0,timeout=5500)
        expect(page.locator('#edit-title')).to_have_value("Unsaved session title")
        action("approve").click()
        expect(action("edit-roadmap")).to_be_visible()
        page.set_viewport_size({"width":390,"height":844})
        action("roadmap-list").click()
        expect(page.get_by_role("button",name="3. Unsaved session title")).to_be_visible()
        assert not errors, errors
        browser.close()
        print("PASS · Chromium setup, regeneration, toast typing, keyboard list, mobile list, reviews, approvals, assistant retry and citations")
