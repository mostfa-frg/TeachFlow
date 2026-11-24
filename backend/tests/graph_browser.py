"""Browser-only check. Run from the repository root with Playwright and Chromium."""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright
from test_graph import proposal

ROOT = Path(__file__).resolve().parents[2]


def run():
    with tempfile.TemporaryDirectory() as temp:
        env = dict(
            os.environ,
            TEACHFLOW_DATA_DIR=temp,
            DATABASE_URL="sqlite:///" + temp + "/test.db",
            PYTHONPATH=os.pathsep.join(
                [str(ROOT / "backend"), str(ROOT / "backend/tests")]
            ),
        )
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=ROOT / "backend",
            env=env,
            check=True,
        )
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "graph_fixture:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=ROOT / "backend",
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", trust_env=False
            ) as api:
                for _ in range(100):
                    try:
                        if api.get("/health").is_success:
                            break
                    except httpx.ConnectError:
                        pass
                    time.sleep(0.05)
                course = (
                    api.post("/api/v1/courses", json={"name": "Graph verification"})
                    .raise_for_status()
                    .json()["id"]
                )
                base = f"/api/v1/courses/{course}/roadmaps"
                version = api.post(base + "/generate").raise_for_status().json()["id"]
                api.post(f"/api/v1/roadmaps/{version}/approve").raise_for_status()
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(
                        executable_path=os.environ.get("TEACHFLOW_CHROMIUM")
                        or shutil.which("chromium"),
                        args=["--no-sandbox", "--disable-dev-shm-usage"],
                    )
                    page = browser.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.set_default_timeout(8000)
                    page.goto(str(api.base_url))
                    page.locator("#course-select").wait_for(state="attached")
                    page.locator("[data-action=roadmap]").first.click()
                    page.locator("[data-action=edit-roadmap]").click()
                    page.locator(
                        "[data-action=select-node][data-id=practice-session]"
                    ).click()
                    page.locator(
                        "[data-action=remove-prereq][data-type=reinforces]"
                    ).click()
                    # Choose a relationship through the actual editor controls.
                    page.locator("#prereq-picker").select_option(
                        "foundation-practice", force=True
                    )
                    page.locator("#link-kind").select_option("extends", force=True)
                    page.locator("#link-note").fill("Edited in the browser")
                    page.locator("[data-action=add-prereq]").click()
                    page.locator("[data-action=approve]").click()
                    page.locator("[data-action=edit-roadmap]").wait_for()
                    page.reload()
                    page.locator("#course-select").wait_for(state="attached")
                    page.locator("[data-action=roadmap]").first.click()
                    page.locator(
                        "[data-action=select-node][data-id=practice-session]"
                    ).click()
                    expected = proposal()["session_edges"]
                    expected[-1].update(
                        edge_type="extends", note="Edited in the browser"
                    )
                    actual = (
                        api.get(base + "/approved")
                        .raise_for_status()
                        .json()["session_edges"]
                    )
                    assert sorted(actual, key=str) == sorted(expected, key=str), actual
                    panel = page.locator("#session-detail-panel")
                    assert (
                        "Edited in the browser" in panel.inner_text()
                        and "extends" in panel.inner_text()
                    )
                    assert "depends_on" in panel.inner_text()
                    page.locator(
                        "[data-action=select-node][data-id=foundation-practice]"
                    ).click()
                    assert "prerequisite" in panel.inner_text() and not errors, errors
                    browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == "__main__":
    run()
    print("Three typed links survived browser edit, approval and refresh.")
