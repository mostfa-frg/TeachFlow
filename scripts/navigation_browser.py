"""Exercise native transitions, the fallback and reduced motion against the fixture server."""

from playwright.sync_api import expect


def verify_navigation(browser, url):
    for mode in ("native", "fallback", "reduced"):
        page = browser.new_page(
            viewport={"width": 820, "height": 620},
            reduced_motion="reduce" if mode == "reduced" else "no-preference",
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_default_timeout(8000)
        page.add_init_script("""window.transitionCalls = 0;
            const native = document.startViewTransition?.bind(document);
            if (native) document.startViewTransition = callback => {
                window.transitionCalls++;
                return native(callback);
            };""")
        if mode == "fallback":
            page.add_init_script("document.startViewTransition = undefined")
        try:
            page.goto(url)
            expect(page.locator("#course-select-trigger")).to_be_visible()
            page.evaluate("""window.chromeNodes = ['.sidebar','.topbar','#course-select-trigger']
                .map(selector => document.querySelector(selector))""")
            page.locator('.nav [data-action="assistant"]').click()
            question = page.get_by_label("Question", exact=True)
            question.fill("Keep my unsent question")
            page.locator('.nav [data-action="roadmap"]').click()
            graph = page.locator("#roadmap-scroll")
            expect(graph).to_be_visible()
            page.get_by_role("button", name="Zoom in", exact=True).click()
            saved = graph.evaluate("""async el => {
                await Promise.all(el.querySelector('#roadmap-inner').getAnimations().map(a=>a.finished));
                el.scrollTo({left:87, top:18, behavior:'instant'});
                window.savedGraph=el;
                return [el.scrollLeft,el.scrollTop,el.querySelector('#roadmap-inner').dataset.zoom];
            }""")
            page.locator('[data-action="toggle-detail"]').click()
            assert graph.evaluate("el => el === window.savedGraph")
            assert page.evaluate("window.chromeNodes.every(el => el.isConnected)")
            page.locator('.nav [data-action="materials"]').click()
            expect(page.get_by_role("heading", name="functions.md")).to_be_visible()
            page.locator('.nav [data-action="roadmap"]').click()
            expect(graph).to_be_visible()
            assert graph.evaluate("""el => [el.scrollLeft,el.scrollTop,
                el.querySelector('#roadmap-inner').dataset.zoom]""") == saved
            page.locator('.nav [data-action="assistant"]').click()
            expect(question).to_have_value("Keep my unsent question")
            assert page.evaluate("window.chromeNodes.every(el => el.isConnected)")
            if mode == "fallback":
                held = []
                page.route("**/api/v1/courses", lambda route: held.append(route), times=1)
                with page.expect_request(lambda req: req.url.endswith("/api/v1/courses")):
                    page.locator('.nav [data-action="materials"]').click()
                expect(page.locator('.skeleton-row').first).to_be_visible()
                page.locator('.nav [data-action="roadmap"]').click()
                page.locator('[data-action="new-course"]').click()
                name = page.locator('#name')
                name.fill("Navigation rehearsal")
                name.evaluate("el => { window.editing = el; el.setSelectionRange(4, 8); }")
                held[0].fulfill(status=503, json={"error": {"message": "Local refresh check"}})
                expect(page.get_by_role("alert")).to_contain_text("Local refresh check")
                assert name.evaluate("""el => el === window.editing && el === document.activeElement
                    && el.selectionStart === 4 && el.selectionEnd === 8""")
                expect(name).to_have_value("Navigation rehearsal")
                page.locator('.nav [data-action="materials"]').click()
                page.locator('.nav [data-action="roadmap"]').click()
                page.locator('[data-action="new-course"]').click()
                expect(name).to_have_value("Navigation rehearsal")
                page.locator('[data-action="continue"]').click()
                expect(page.locator("#calendar-file")).to_be_attached()
                assert page.evaluate("document.documentElement.style.getPropertyValue('--slide')") == "9px"
                page.locator('[data-action="back"]').click()
                expect(name).to_be_visible()
                assert page.evaluate("document.documentElement.style.getPropertyValue('--slide')") == "-9px"
            if mode == "native" and page.evaluate("Boolean(document.startViewTransition)"):
                assert page.evaluate("window.transitionCalls > 0")
            if mode == "reduced":
                assert page.evaluate("window.transitionCalls === 0")
                assert page.locator(".content").evaluate("el => el.getAnimations({subtree:true}).length === 0")
            assert not errors, errors
        finally:
            page.close()
    print("PASS · stable shell, draft text, roadmap zoom/pan and motion preferences")
