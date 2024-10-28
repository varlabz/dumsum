import argparse
import os
import yaml
from playwright.sync_api import sync_playwright, Playwright
from chat import answer
from chat import matcher
from common import *
from defaults import Defaults
from linkedin_easy_apply import easy_apply_form

def get_job_title(page):
    if l := locator_exists(page, 'a.job-card-list__title'):
        return ' '.join(l.text_content().split())
    if l := locator_exists(page, 'a.job-card-job-posting-card-wrapper__card-link'):
        return ' '.join(l.text_content().split())
    return None

def use_matcher(job: str) -> bool: 
    if config().matcher:
        match = matcher(job) 
        print(f">>> matcher: {match}")
        if match is None:
            return False
        return int(float(match['match'])) >= config().matcher
    else:
        return True

def job_positions(page, defaults: Defaults, easy_apply_form):
    plist = page.locator('ul.scaffold-layout__list-container > li.jobs-search-results__list-item').all()
    print(f"# positions: {len(plist)}")
    for i in plist:
        if locator_exists(i, 'button[aria-label$="job is dismissed, undo"]'):
            print(f">>> skip: {get_job_title(i)}")
            continue
        # print(f'>>> position {i.locator('a[label]')}')
        i.click()
        page.wait_for_timeout(1_000)
        detail = page.locator('div.scaffold-layout__detail')
        job_description = detail.locator('article.jobs-description__container >> div.mt4').text_content().strip()
        # print(f">>> job description: {job_description}")
        if not use_matcher(job_description):
            continue
        try:
            ea = detail.locator("button >> span:text-is('Easy Apply')").all()[0]   # take 1st (for some reason have 2 buttons)
        except (TimeoutError, IndexError) as ex:
            continue
        # print(f"easy apply:: {ea}")
        print(f">>> use '{get_job_title(i)}'", )    
        ea.click()
        page.wait_for_timeout(1_000)
        progress = -1   # use to track current page, if page
        if easy_apply_form(page, defaults, progress):
            defaults.save()
            print(">>> easy apply form done")
            try:
                page.wait_for_timeout(3_000)
                page.wait_for_selector('div[role="dialog"]')
                page.locator('div[role="dialog"]').locator('button[aria-label="Dismiss"]').click()
            except Exception as ex:
                print(f"error: {ex}")
            i.locator('button.job-card-container__action-small').click() # do not show the position again, click on cross
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

def config():
    parser = argparse.ArgumentParser(description="LinkedIn Easy Apply Bot")
    parser.add_argument("--matcher", type=int, required=False, help="Use resume matcher to filter job positions. Specify a percentage (0-100) for matching threshold.")
    parser.add_argument("--debug-easy-apply-form", action='store_true', default=False, required=False, help="Debug")
    args = parser.parse_args()
    return args

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

            job_paginator(page, defaults, job_positions)
            defaults.save()
            print(f"done")
            return
    print(">>> linkedin.com/jobs/ not found")

with sync_playwright() as playwright:
    run(playwright)
