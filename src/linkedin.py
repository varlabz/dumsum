import os
from playwright.sync_api import sync_playwright, Playwright
from chat import matcher
from common import *
from defaults import Defaults
from linkedin_easy_apply import easy_apply_form

def get_job_title(page):
    if l := locator_exists(page, 'a.job-card-list__title >> span[aria-hidden="true"]'):
        return ' '.join(l.text_content().split())
    if l := locator_exists(page, 'a.job-card-job-posting-card-wrapper__card-link'):
        return ' '.join(l.text_content().split())
    return None

def set_match(page, match):
    if l := locator_exists(page, 'a.job-card-list__title >> span[aria-hidden="true"] >> strong'):
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
    plist = page.locator('ul.scaffold-layout__list-container > li.jobs-search-results__list-item').all()
    print(f"# positions: {len(plist)}")
    for p in plist:
        if locator_exists(p, 'button[aria-label$="job is dismissed, undo"]'):
            print(f">>> skip: {get_job_title(p)}")
            continue
        p.click()
        page.wait_for_timeout(1_000)
        detail = page.locator('div.scaffold-layout__detail')
        job_description = detail.locator('article.jobs-description__container >> div.mt4').text_content().strip()
        print(f">>> use '{get_job_title(p)}'", )    
        try:
            easy_apply_btn = detail.locator("button >> span:text-is('Easy Apply')").all()[0]   # take 1st (for some reason have 2 buttons)
        except (TimeoutError, IndexError) as ex:
            continue
        (match, skip) = use_matcher(job_description)
        set_match(p, match)
        if 1 <= int(match) <= config().matcher_ignore:
            p.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
            print(">>> don't show position again. match is too low")
        if skip:
            continue
        easy_apply_btn.click()
        progress = -1   # use to track current page, if page
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
        for p in new_pages:
            curr = int(p.get_attribute('data-test-pagination-page-btn'))
            # print(f">>> new page: {curr}")
            p.click()
            page.wait_for_timeout(1_000)
            job_positions(page, defaults, easy_apply_form)
    else:
        job_positions(page, defaults, easy_apply_form)

def run(engine: Playwright):
    if hasattr(config(), 'help'):
        return
    
    chromium = engine.chromium
    browser = chromium.connect_over_cdp(os.getenv('CDP_HOST', 'http://localhost:9222'))
    for page in browser.contexts[0].pages:
        if page.url.startswith('https://www.linkedin.com/jobs/'):
            print(f">>> linkedin.com/jobs/ found")
            defaults = Defaults()
            if config().debug_easy_apply_form:
                easy_apply_form(page, defaults, -1)
                return
            if config().debug_1page:
                job_positions(page, defaults, easy_apply_form)
            else:    
                job_paginator(page, defaults, job_positions)
            print(f"done")
            return
    print(">>> linkedin.com/jobs/ not found")

with sync_playwright() as playwright:
    run(playwright)
