import os
from playwright.sync_api import sync_playwright, Playwright

def delay_call(page, callback, delay=5_000):
    page.wait_for_timeout(delay)
    callback()

def if_locator_exists(page, selector):
    return page.locator(selector).count() > 0

def optional_locator(page, field, callback):
    try:
        if not if_locator_exists(page, field):
            return None
        
        e = page.locator(field)
        # print(f"### optional_locator: {e} for {field}")
        if e is None:
            return None     
        callback(e)
        return e 
    except Exception as ex:
        print(f"error: {ex}")

    return None

def easy_apply_form(page) -> bool:
    print(">>> start easy apply form")
    while True:
        try:
            page.wait_for_timeout(5_000)
            page.wait_for_selector('div[role="dialog"]', state="visible")
            dialog = page.locator('div[role="dialog"]')
            # check empty fields
            req = dialog.locator('input[required]').all()
            # print(f"# required: {len(req)}")
            for i in req:
                if not i.input_value().strip():
                    print(f">>> required field is empty")
                    page.wait_for_timeout(5_000)

            if optional_locator(dialog, 'button >> span:text-is("Next")', lambda x: x.click()):
                print(">>> next")
                continue

            if optional_locator(dialog, 'button >> span:text-is("Review")', lambda x: x.click()):
                print(">>> review")
                continue

            ## optional_locator(dialog, 'input[id="follow-company-checkbox"][type="checkbox"]',   ## doesn't work use hack with javascript
            ##                 lambda x: x.click()) ##if x.is_checked() else None)
            if if_locator_exists(dialog, 'input[id="follow-company-checkbox"][type="checkbox"]'):
                dialog.evaluate('document.getElementById("follow-company-checkbox").checked=false')
                # optional_locator(dialog, 'input[id="follow-company-checkbox"][type="checkbox"]',
                #             lambda x: print(f"### follow checkbox {x.is_checked()}"))

            if if_locator_exists(dialog, 'button >> span:text-is("Submit application")'):
                print(">>> ready to submit")
                page.wait_for_timeout(5_000)
                optional_locator(dialog, 'button >> span:text-is("Submit application")', lambda x: x.click())
                print(">>> submit")
                return True

        except Exception as ex:
            print(f"error: {ex}")
            return False

def get_job_title(page):
    return ' '.join(page.locator('a.job-card-list__title').text_content().split())

def job_positions(page):
    list = page.locator('ul.scaffold-layout__list-container > li.jobs-search-results__list-item').all()
    print(f"# positions: {len(list)}")
    for i in list:
        if if_locator_exists(i, 'button[aria-label$="job is dismissed, undo"]'):
            print(f">>> skip: {get_job_title(i)}")
            continue
        # print(f'>>> position {i.locator('a[label]')}')
        i.click()
        page.wait_for_timeout(1_000)
        detail = page.locator('div.scaffold-layout__detail')
        try:
            ea = detail.locator("button >> span:text-is('Easy Apply')").all()[0]   # take 1st (for some reason have 2 buttons)
        except (TimeoutError, IndexError) as ex:
            continue

        # print(f"easy apply:: {ea}")
        print(f">>> use '{get_job_title(i)}'", )    
        ea.click()
        page.wait_for_timeout(1_000)
        if easy_apply_form(page):
            print(">>> easy apply form done")
            try:
                page.wait_for_timeout(3_000)
                page.wait_for_selector('div[role="dialog"]')
                page.locator('div[role="dialog"]').locator('button[aria-label="Dismiss"]').click()
            except Exception as ex:
                print(f"error: {ex}")
            i.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            print(">>> don't show position again")
            print(">>> easy apply continue")
        else:
            print(">>> easy apply form failed")

        print(">>> next position")

def run(playwright: Playwright):
    chromium = playwright.chromium 
    browser = chromium.connect_over_cdp(os.getenv('CDP_HOST', 'http://localhost:9222'))
    for page in browser.contexts[0].pages:
        if page.url.startswith('https://www.linkedin.com/jobs/'):
            job_positions(page)
            print(f"done")
            return
    
    print(">>> linkedin.com/jobs/ not found")

with sync_playwright() as playwright:
    run(playwright)
