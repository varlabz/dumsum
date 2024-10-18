from playwright.sync_api import sync_playwright, Playwright

def optional_locator(page, field, callback):
    try:
        e = page.locator(field)
        # print(f"### optional_locator: {e} for {field}")
        if e is None:
            return None     
        callback(e)
        return e 
    except Exception:
        pass
    return None

def easy_apply_form(page) -> bool:
    print(">>> start easy apply form")
    while True:
        try:
            page.wait_for_selector('div[role="dialog"]', state="visible")
            dialog = page.locator('div[role="dialog"]')
            # check empty fields if have any then stop
            req = dialog.locator('input[required]').all()
            print(f"# required: {len(req)}")
            # for i in req:
            #     if not i.input_value().strip():
            #         print(f"required field is empty: {i}")

            if optional_locator(dialog, 'button >> span:text-is("Next")', lambda x: x.click()):
                page.wait_for_timeout(2_000)
                continue

            if optional_locator(dialog, 'button >> span:text-is("Review")', lambda x: x.click()):
                continue

            ## optional_locator(dialog, 'input[id="follow-company-checkbox"][type="checkbox"]',   ## doesn't work use hack with javascript
            ##                 lambda x: x.click()) ##if x.is_checked() else None)
            dialog.evaluate('document.getElementById("follow-company-checkbox").checked=false') 
            optional_locator(dialog, 'input[id="follow-company-checkbox"][type="checkbox"]',
                            lambda x: print(f"### follow checkbox {x.is_checked()}"))
            if optional_locator(dialog, 'button >> span:text-is("Submit application")', lambda x: x.click()):
                return True
        except Exception:
            return False


def job_positions(page):
    list = page.locator('ul.scaffold-layout__list-container > li.jobs-search-results__list-item').all()
    print(f"# positions: {len(list)}")
    for i in list:
        # print(f'>>> position {i.locator('a[label]')}')
        i.click()
        page.wait_for_timeout(1_000)
        detail = page.locator('div.scaffold-layout__detail')
        try:
            ea = detail.locator("button >> span:text-is('Easy Apply')").all()[0]   # take 1st (for some reason have 2 buttons)
        except (TimeoutError, IndexError):
            continue

        # print(f"easy apply:: {ea}")
        print(f">>> use '{' '.join(i.locator('a.job-card-list__title').text_content().split())}'", )    
        ea.click()
        page.wait_for_timeout(1_000)
        if easy_apply_form(page):
            print(">>> easy apply form done")
            i.locator('button.job-card-container__action-small').click() # want to not show the position again, click on cross
            try:
                page.wait_for_timeout(1_000)
                page.wait_for_selector('div[role="dialog"]', timeout=20_000)
                # page.get_by_text('Application sent').locator('button[aria-label="Dismiss"]').click()
                page.locator('div[role="dialog"]').locator('button[aria-label="Dismiss"]').click()
                # page.locator('div[role="dialog"][data-test-modal]').locator('button[aria-label="Dismiss"]').click()
                # page.locator('div[role="dialog"][data-test-modal]').locator('button >> span:text-is("Dismiss")').click()
            except TimeoutError:
                print(">>> easy apply continue")
        else:
            print(">>> easy apply form failed")
        print(">>> next")

def run(playwright: Playwright):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = chromium.connect_over_cdp("http://host.docker.internal:9222") # 'http://localhost:9222') # 
    for page in browser.contexts[0].pages:
        if page.url.startswith('https://www.linkedin.com/jobs/'):
            job_positions(page)
            print(f"DONE")

with sync_playwright() as playwright:
    run(playwright)
