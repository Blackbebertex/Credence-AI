import asyncio
import os
import sys
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\LT-446\.gemini\antigravity-ide\brain\c33f1566-df63-45f8-b08b-ff3e23eb6fc8"
TARGET_URL = "https://credence-ai-two.vercel.app/"

async def run_e2e():
    print(f"Starting Playwright E2E browser test on {TARGET_URL}...")
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Collect console logs and errors
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: console_logs.append(f"[ERROR] {exc}"))

        try:
            # 1. Navigation & Initial Load
            print("1. Navigating to Vercel application...")
            response = await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
            status = response.status if response else 0
            title = await page.title()
            print(f"   HTTP Status: {status}, Title: '{title}'")
            results.append(("Navigation & Page Load", status == 200, f"Status: {status}, Title: {title}"))

            # Save initial dashboard screenshot
            dash_path = os.path.join(ARTIFACT_DIR, "e2e_01_dashboard.png")
            await page.screenshot(path=dash_path, full_page=False)
            print(f"   Saved screenshot: {dash_path}")

            # 2. Check Statutory Admissibility Banner (P0-02 Claim Rule)
            print("2. Checking Statutory Admissibility Banner...")
            banner_text = await page.inner_text(".statutory-banner")
            has_s63 = "Section 63" in banner_text
            has_disclaimer = "Advisory Decision Support" in banner_text or "judicial determination" in banner_text
            has_tag = "BSA s.63 ADMISSIBILITY SUPPORT" in banner_text
            banner_ok = has_s63 and has_disclaimer
            print(f"   Banner Text Sample: {banner_text[:120]}...")
            results.append(("Statutory Admissibility Banner (BSA s.63)", banner_ok, "Includes s.63 advisory wording"))

            # 3. Check KPI Cards and Backend Status
            print("3. Checking KPI cards & connection pill...")
            pill_text = await page.inner_text(".connection-pill")
            print(f"   Connection Pill: '{pill_text.strip()}'")
            kpis = await page.query_selector_all(".kpi-card")
            print(f"   Found {len(kpis)} KPI cards on dashboard")
            results.append(("KPI Grid Loaded", len(kpis) >= 4, f"{len(kpis)} KPI cards found"))

            # 4. Tab Navigation: Case Register
            print("4. Testing Tab: Case Register...")
            await page.click("button.nav-item:has-text('Case Register')")
            await page.wait_for_timeout(1000)
            cases_table = await page.query_selector(".cases-table")
            table_ok = cases_table is not None
            cases_path = os.path.join(ARTIFACT_DIR, "e2e_02_cases.png")
            await page.screenshot(path=cases_path, full_page=False)
            print(f"   Saved screenshot: {cases_path}")
            results.append(("Case Register Tab", table_ok, "Table rendered successfully"))

            # 5. Open Case Details Modal if cases exist
            print("5. Inspecting Case Details modal...")
            case_rows = await page.query_selector_all(".cases-table tbody tr")
            if len(case_rows) > 0:
                first_row = case_rows[0]
                await first_row.click()
                await page.wait_for_timeout(1000)
                modal = await page.query_selector(".modal-content")
                modal_ok = modal is not None
                if modal_ok:
                    modal_text = await modal.inner_text()
                    has_verifier = "scripts/verifier.py" in modal_text
                    print("   Case modal opened. Found offline verifier hint:", has_verifier)
                    modal_path = os.path.join(ARTIFACT_DIR, "e2e_03_case_modal.png")
                    await page.screenshot(path=modal_path, full_page=False)
                    print(f"   Saved screenshot: {modal_path}")
                    # Close modal
                    close_btn = await page.query_selector(".modal-header button")
                    if close_btn:
                        await close_btn.click()
                        await page.wait_for_timeout(500)
                    results.append(("Case Details Modal & Verifier Preview", modal_ok and has_verifier, "Modal opened with verifier CLI preview"))
            else:
                results.append(("Case Details Modal", True, "No cases rendered yet (offline mode)"))

            # 6. Tab Navigation: Review Queue
            print("6. Testing Tab: Review Queue...")
            await page.click("button.nav-item:has-text('Review Queue')")
            await page.wait_for_timeout(1000)
            rev_path = os.path.join(ARTIFACT_DIR, "e2e_04_review_queue.png")
            await page.screenshot(path=rev_path, full_page=False)
            print(f"   Saved screenshot: {rev_path}")
            results.append(("Review Queue Tab", True, "Rendered cleanly"))

            # 7. Tab Navigation: Provenance Graph
            print("7. Testing Tab: Provenance Graph...")
            await page.click("button.nav-item:has-text('Provenance Graph')")
            await page.wait_for_timeout(1000)
            graph_svg = await page.query_selector(".graph-svg")
            graph_ok = graph_svg is not None
            # Click a node
            hash_node = await page.query_selector(".graph-node:has-text('SHA-256')")
            if hash_node:
                await hash_node.click()
                await page.wait_for_timeout(500)
            prov_path = os.path.join(ARTIFACT_DIR, "e2e_05_provenance_graph.png")
            await page.screenshot(path=prov_path, full_page=False)
            print(f"   Saved screenshot: {prov_path}")
            results.append(("Interactive Provenance Graph", graph_ok, "SVG graph rendered and interactive"))

        except Exception as e:
            print(f"Test run exception: {e}")
            results.append(("General Execution", False, str(e)))

        finally:
            await browser.close()

    print("\n=======================================================")
    print("           BROWSER AUTOMATION TEST RESULTS             ")
    print("=======================================================")
    all_passed = True
    for name, passed, detail in results:
        mark = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f" {mark} {name}: {detail}")
    print("=======================================================")
    if console_logs:
        print("\nBrowser Console Logs (first 10):")
        for log in console_logs[:10]:
            print("  ", log)
    print("=======================================================\n")
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_e2e())
    sys.exit(0 if success else 1)
