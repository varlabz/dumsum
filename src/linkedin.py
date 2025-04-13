import os
from playwright.sync_api import sync_playwright, Playwright
from chat import matcher
from common import *
from defaults import Defaults
import linkedin_easy_apply as easy_apply

def get_job_title(page):
    if l := locator_exists(page, 'a.job-card-list__title--link >> span[aria-hidden="true"]'):
        return ' '.join(l.text_content().split())
    if l := locator_exists(page, 'a.job-card-job-posting-card-wrapper__card-link'):
        return ' '.join(l.text_content().split())
    return None

def get_job_company(page):
    if l := locator_exists(page, 'div.artdeco-entity-lockup__subtitle'):
        return 'Company: ' + ' '.join(l.text_content().split())
    return ''

def set_match(page, match):
    if l := locator_exists(page, 'a.job-card-list__title--link >> span[aria-hidden="true"] >> strong'):
        l.evaluate(f"(element) => element.innerText += ' [{match}%]'")

def use_matcher(job: str) -> tuple[str, bool]: 
    if config().matcher:
        match = matcher(job) 
        print(f">>> matcher: {match}")
        if match is None:
            return ('?', True)
        match = int(float(match['match']))
        if config().debug_matcher:
            print(f">>> --debug-matcher is on")
            return (match, True)
        return (match, match < config().matcher)
    else:
        return (0, False)

def job_positions(page, defaults: Defaults, easy_apply_form):
    plist = page.locator('ul > li.scaffold-layout__list-item').all()
    print(f"# positions: {len(plist)}")
    for p in plist:
        if locator_exists(p, 'button[aria-label$="job is dismissed, undo"]'):
            print(f">>> skip: {get_job_title(p)}")
            continue
        if locator_exists(p, 'ul > li:has-text("Applied")'): # do not show the position again, click on cross
            print(">>> skip: already applied")
            if loc := locator_exists(p, 'button.job-card-container__action-small'):
                if locator_exists(p, 'svg[data-test-icon="close-small"]'):
                    loc.click() 
            continue
        job_company = get_job_company(p)
        # print(f"#### {job_company}")
        p.click()
        page.wait_for_timeout(1_000)
        detail = page.locator('div.scaffold-layout__detail')
        if btn := locator_exists(detail, 'button[aria-label^="see more,"]', has_text=r'show more'):
            btn.click()
            page.wait_for_timeout(1_000)
        job_description = ' '.join(detail.locator('div.job-details-about-the-job-module__description').text_content().strip()) + job_company
        print(f">>> use '{get_job_title(p)}'", )    
        (match, skip) = use_matcher(job_description)
        set_match(p, match)
        if 1 <= int(match) <= config().matcher_ignore:
            p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            print(">>> don't show position again. match is too low")
        if skip:
            continue
        if btn := locator_exists(detail, "button", has_text=r'Apply',):     # regex doesn't work with text
            applied = False
            for b in btn.all():
                if b.text_content().strip() == 'Apply':
                    if config().click_apply:
                        print(">>> click apply")
                        b.click()
                        p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
                    applied = True
                    break
            if applied:
                continue
        if btn := locator_exists(detail, "button", has_text=r'Easy Apply',):    # regex doesn't work with text
            applied = False
            for b in btn.all():
                if b.text_content().strip() == 'Easy Apply':
                    if config().click_easy_apply:
                        print(f">>> click easy apply")
                        b.click()
                    else:
                        applied = True
                    break
            if applied:
                continue
        else:
            print(">>> can't apply")
            p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            continue
        # for easy apply form
        progress = -1   # use to track current page
        defaults.load()
        if easy_apply_form(page, defaults, progress):
            defaults.save()
            print(">>> easy apply form done")
            try:
                page.wait_for_timeout(2_000)
                page.wait_for_selector('div[role="dialog"]')
                page.locator('div[role="dialog"]').locator('button[aria-label="Dismiss"]').click()
            except Exception as ex:
                print(f"error: {ex}")
            p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            print(">>> don't show position again")
        else:
            print(">>> easy apply form failed")
        print(">>> next position")

def job_paginator(page, defaults: Defaults, job_positions):
    page.wait_for_timeout(1_000)
    if locator_exists(page, 'div.jobs-search-results-list__pagination'):
        pages = page.locator('div.jobs-search-results-list__pagination >> li[data-test-pagination-page-btn]').all()
        # print(f"# pages: {len(pages)}")
        have_current = -1
        new_pages = []
        for p in pages:     # copy the rest links from current selection 
            curr = int(p.get_attribute('data-test-pagination-page-btn'))
            # print(f">>> page: {curr}")
            if p.locator('button[aria-current="true"]').count() > 0:
                have_current = int(curr)
                new_pages.append(p)
            if have_current == -1:
                continue    
            if curr == (have_current + 1):
                new_pages.append(p)
            have_current = int(curr)
        # print(f"# new pages: {len(new_pages)}")    
        max_pages = int(config().max_pages)
        for p in new_pages:
            max_pages -= 1
            if max_pages < 0:
                break
            curr = int(p.get_attribute('data-test-pagination-page-btn'))
            # print(f">>> new page: {curr}")
            p.click()
            page.wait_for_timeout(1_000)
            job_positions(page, defaults, easy_apply.easy_apply_form)
    else:
        job_positions(page, defaults, easy_apply.easy_apply_form)

def run(engine: Playwright):
    if hasattr(config(), 'help'):
        return
    
    chromium = engine.chromium
    browser = chromium.connect_over_cdp(os.getenv('CDP_HOST', 'http://localhost:9222'))
    for page in browser.contexts[0].pages:
        if page.url.startswith('https://www.linkedin.com/jobs/'):
            print(f">>> linkedin.com/jobs/ found")
            def back_handle_click(x, y):
                # if back button clicked, wait for 30 seconds for review
                print(f">>> back button clicked")
                easy_apply.TIMEOUT = 30_000    
            page.expose_function("back_handle_click", back_handle_click)
            defaults = Defaults()
            if config().debug_easy_apply_form:
                defaults.load()   
                easy_apply.easy_apply_form(page, defaults, -1)
                return
            if config().debug_1page:
                job_positions(page, defaults, easy_apply.easy_apply_form)
            else:    
                job_paginator(page, defaults, job_positions)
            print(f"done")
            return
    print(">>> linkedin.com/jobs/ not found")

with sync_playwright() as playwright:
    if os.path.exists(".key"):
        from dotenv import load_dotenv
        load_dotenv(".key")
        
    run(playwright)
