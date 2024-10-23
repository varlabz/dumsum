import os
import yaml
from playwright.sync_api import sync_playwright, Playwright

# def delay_call(page, callback, delay=5_000):
#     page.wait_for_timeout(delay)
#     callback()

def locator_exists(page, selector):
    return page.locator(selector).count() > 0

def optional_locator(page, field, callback):
    try:
        if not locator_exists(page, field):
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

# hack. sometimes selector has 2 spans with the same text. use 1 only
def remove2(text: str):
    mid = len(text) // 2
    half1 = text[:mid]
    half2 = text[mid:]
    if  half1 == half2:
        return half1
    else:
        return text

def get_label(el, ):
    if el.locator('..').locator('label').count() > 0:
        el = el.locator('..').locator('label')
    elif el.locator('..').locator('..').locator('label').count() > 0: # sometimes need to check 1 level up
        el = el.locator('..').locator('..').locator('label')
    return remove2(' '.join(el.text_content().split()))

def check_required(page, dialog, defaults: dict, init):
    def check_radio(el):
        v = el.get_attribute("value")
        if init:
            if defaults.get(v, False):
                i.check()
        else:
            if i.is_checked():
                defaults[v] = True
            else:
                defaults.pop(v, False)

    # check empty fields
    req = dialog.locator('input[required],input[aria-required="true"]').all()
    print(f"# input required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # print(f">>> required input: '{label}'='{val}' /// {defaults.get(label, None)}")
        if i.get_attribute('type') == "radio":  # special case for radio buttons
            #check_radio(i) # TODO do it right way. use label and radio buttons as values
            pass
        else:
            if init:
                if defaults.get(label, None):
                    i.fill(defaults.get(label))
            else:
                if not val:
                    print(f">>> required input is empty: '{label}'")
                    page.wait_for_timeout(5_000)
                else:
                    defaults[label] = val

    req = dialog.locator('select[required],select[aria-required="true"]').all()
    print(f"# select required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # hack: get a selected index from selector
        selected_index = page.eval_on_selector(f'select#{i.get_attribute("id")}', "select => select.selectedIndex")
        # print(f">>> required select: '{label}'='{val}':{selected_index}///{defaults.get(label, None)}")
        if init:
            if defaults.get(label, None):
                i.select_option(defaults.get(label))
        else:
            if selected_index == 0:
                page.wait_for_timeout(5_000)
            else:
                defaults[label] = val

DEFAULTS = "data/defaults.yaml"

def save_defaults(defaults: dict):
    with open(DEFAULTS, "w") as file:
        yaml.dump(defaults, file, default_flow_style=False, sort_keys=False)

def easy_apply_form(page, defaults: dict, progress: int) -> bool:
    # progress: -1 very first start, 0 - 1st page, 100 - last page
    # click easy apply button
    print(">>> start easy apply form")
    while True:
        try:
            page.wait_for_timeout(5_000)
            page.wait_for_selector('div[role="dialog"]', state="visible")
            dialog = page.locator('div[role="dialog"]')

            if locator_exists(dialog, 'progress[value]'):
                current_progress = int(float(dialog.locator('progress[value]').get_attribute('value')))
                # print(f">>> progress: {current_progress} -> {progress}")
                init = progress != current_progress     # first time on page, get fields from defaults
                progress = current_progress
            else:   # don't have progress bar
                init = False

            check_required(page, dialog, defaults, init)
            save_defaults(defaults)

            if optional_locator(dialog, 'button >> span:text-is("Skip")', lambda x: x.click()):
                print(">>> skip")
                continue

            if optional_locator(dialog, 'button >> span:text-is("Next")', lambda x: x.click()):
                print(">>> next")
                continue

            if optional_locator(dialog, 'button >> span:text-is("Review")', lambda x: x.click()):
                print(">>> review")
                continue

            def follow_check(label): # hack: can't click, set uncheck, have to use label
                check = optional_locator(dialog, 'input[id="follow-company-checkbox"]', lambda x: x)
                if check and check.is_checked():
                    label.click()

            optional_locator(dialog, 'label[for="follow-company-checkbox"]', lambda x: follow_check(x))

            if locator_exists(dialog, 'button >> span:text-is("Submit application")'):
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

def use_matcher(job: str) -> bool: 
    from chat_groq import matcher
    match = matcher(job) 
    if match is None:
        print(">>> matcher failed")
        return False
    print(f">>> matcher: {match}")
    return int(match['match']) >= 50

# def send_message_to_hiring_team(page):
#     if locator_exists(page, 'div[data-feedback-redacted]'):
#         print(">>> send message to the hiring team")
#         msg = page.locator('div[data-feedback-redacted]')
#         msg.locator('button[msg-form__send-btn][type="submit"]').click()

def job_positions(page, defaults):
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
            save_defaults(defaults)
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
            # send_message_to_hiring_team(page)
        else:
            print(">>> easy apply form failed")

        print(">>> next position")

def run(engine: Playwright):
    chromium = engine.chromium
    browser = chromium.connect_over_cdp(os.getenv('CDP_HOST', 'http://localhost:9222'))
    for page in browser.contexts[0].pages:
        if page.url.startswith('https://www.linkedin.com/jobs/'):
            print(f">>> linkedin.com/jobs/ found")
            defaults = {}
            if not os.path.exists(DEFAULTS):
                save_defaults(defaults)
            with open(DEFAULTS, "r") as file:
                defaults = yaml.safe_load(file)
            job_positions(page, defaults)
            save_defaults(defaults)
            print(f"done")
            return
    
    print(">>> linkedin.com/jobs/ not found")

with sync_playwright() as playwright:
    run(playwright)
