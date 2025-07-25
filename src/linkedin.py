import os
from typing_extensions import Final
from playwright.sync_api import sync_playwright, Playwright
from chat import IGNORE_FILE, URLS_FILE, matcher
from common import *
from defaults import Defaults
import linkedin_easy_apply as easy_apply
from job_application_records import JobApplicationRecords, JobApplicationRecordsSQLite

jobApplicationRecords: Final = JobApplicationRecordsSQLite()

def filter_company(job_company):
    """Filter out ignored company and dismiss the position"""
    ignored_companies = set()
    if os.path.exists(IGNORE_FILE):
        with open(IGNORE_FILE, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignored_companies.add(line.lower())
    return job_company.lower() in ignored_companies

def get_job_title(page):
    if l := locator_exists(page, 'a.job-card-list__title--link >> span[aria-hidden="true"]'):
        return ' '.join(l.text_content().split())
    if l := locator_exists(page, 'a.job-card-job-posting-card-wrapper__card-link'):
        return ' '.join(l.text_content().split())
    return None

def get_job_company(page): 
    if l := locator_exists(page, 'div.artdeco-entity-lockup__subtitle'):
        return ' '.join(l.text_content().split())

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
    # print(f"# positions: {len(plist)}")
    for p in plist:
        p.scroll_into_view_if_needed()
        page.wait_for_timeout(1_000)

        job_company = get_job_company(p)
        job_title = get_job_title(p)

        if filter_company(job_company):
            print(f">>> skip: ignored company - {job_company}")
            if loc := locator_exists(p, 'button.job-card-container__action-small'):
                if locator_exists(p, 'svg[data-test-icon="close-small"]'):
                    loc.click()
            continue

        if locator_exists(p, 'button[aria-label$="job is dismissed, undo"]'):
            print(f">>> skip: {job_title}")
            continue

        if locator_exists(p, 'ul > li:has-text("Applied")'): # do not show the position again, click on cross
            print(">>> skip: already applied")
            if loc := locator_exists(p, 'button.job-card-container__action-small'):
                if locator_exists(p, 'svg[data-test-icon="close-small"]'):
                    loc.click() 
            continue

        if not jobApplicationRecords.should_apply(job_title, job_company):
            print(f">>> skip: already applied to {job_title} at {job_company}")
            if loc := locator_exists(p, 'button.job-card-container__action-small'):
                if locator_exists(p, 'svg[data-test-icon="close-small"]'):
                    loc.click()
            continue

        p.click()
        page.wait_for_timeout(1_000)

        detail = page.locator('div.scaffold-layout__detail')
        if btn := locator_exists(detail, 'button[aria-label^="see more,"]', has_text=r'show more'):
            btn.click()
            page.wait_for_timeout(1_000)
        job_description = "Company: "  + job_company + "\n\n" + \
            ' '.join(detail.locator('div.job-details-about-the-job-module__description').text_content().strip()) 
        print(f">>> use '{get_job_title(p)}' {job_company}", )    
        (match, skip) = use_matcher(job_description)
        set_match(p, match)
        if 1 <= int(match) <= config().matcher_ignore:
            p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            print(">>> don't show position again. match is low")
        if skip:
            continue

        if btn := locator_exists(detail, "button", has_text=r'Apply',):     # regex doesn't work with text
            applied = False
            for b in btn.all():
                if b.text_content().strip() == 'Apply':
                    if config().click_apply:
                        print(">>> click apply")
                        p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
                        b.click()
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
    if locator_exists(page, 'button[aria-label="View next page"]'):
        max_pages = int(config().max_pages)
        for i in range(max_pages):
            # print(f">>> page {i} of {max_pages}")
            job_positions(page, defaults, easy_apply.easy_apply_form)
            if i == max_pages - 1:
                print(f">>> max pages reached: {max_pages}")
                break
            if next := locator_exists(page, 'button[aria-label="View next page"]'):
                next.click()
                page.wait_for_timeout(1_000)
            else:
                print(f">>> no more pages")
                break
    else:
        job_positions(page, defaults, easy_apply.easy_apply_form)

def exec_page(page):
    def back_handle_click(x, y):
        # if back button clicked, wait for 30 seconds for review
        print(f">>> back button clicked")
        easy_apply.TIMEOUT = 30_000    
    page.expose_function("back_handle_click", back_handle_click)
    page.add_locator_handler(
        page.locator('button', has_text=r'Continue applying'),
        lambda locator: locator.click(),
    )
    defaults = Defaults()
    if config().debug_easy_apply_form:
        defaults.load()   
        easy_apply.easy_apply_form(page, defaults, -1)
        return
    if config().debug_1page:
        job_positions(page, defaults, easy_apply.easy_apply_form)
    else:    
        job_paginator(page, defaults, job_positions)

def run(engine: Playwright):
    def try_page():
        for page in browser.contexts[0].pages:
            if page.url.startswith('https://www.linkedin.com/jobs/'):
                print(f">>> linkedin.com/jobs/ found")
                exec_page(page)
                page.close()
                print(f"done")
                return
        print(">>> linkedin.com/jobs/ not found")
        exit(1)
    
    if hasattr(config(), 'help'):
        return

    chromium = engine.chromium
    browser = chromium.connect_over_cdp(os.getenv('CDP_HOST', 'http://localhost:9222'))
    if config().url:
        print(f">>> open {config().url}")
        browser.contexts[0].new_page().goto(config().url)
        try_page()
    elif os.path.exists(URLS_FILE) and not config().debug_no_url:
        with open(URLS_FILE, 'r') as file:
            urls = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        for u in urls:
            print(f">>> open {u}")
            browser.contexts[0].new_page().goto(u)
            try_page()
    else:
        try_page()

with sync_playwright() as playwright:
    if os.path.exists(".key"):
        from dotenv import load_dotenv
        load_dotenv(".key")
        
    run(playwright)
