from common import *
from defaults import Defaults

TIMEOUT = 1_000 if config().speed else 30_000

def fieldset_radio(dialog, defaults: Defaults, init):
    req = dialog.locator('fieldset:has(input[type="radio"][aria-required="true"])').all()
    # print(f"# fieldset: {req}")
    for r in req:
        if l := locator_exists(r, 'legend >> span[aria-hidden="true"]'):
            label = l.text_content().strip()
        else:
            print(f"error: no label for fieldset: {r}")
            continue            
        inputs = r.locator('input[type="radio"][aria-required="true"]').all()
        if init:
            if any((j:=i).is_checked() for i in inputs):
                defaults[label] = j.get_attribute('data-test-text-selectable-option__input')
                continue
            options = [i.get_attribute('data-test-text-selectable-option__input') for i in inputs]
            print(f"### options: {options}")
            if v := defaults.get(label, options):
                print(f">>> answer for: '{label}' is '{v}'")
                if any(((k:=j).get_attribute('data-test-text-selectable-option__input').lower()) == (a:=v['answer'].lower()) for j in inputs):
                    k.locator('..').locator('label').click()    # direct click on radio doesn't work
        if any((j:=i).is_checked() for i in inputs):
            defaults[label] = j.get_attribute('data-test-text-selectable-option__input')

def fieldset_checkbox(dialog, defaults: Defaults, init):
    req = dialog.locator('fieldset:has(input[type="checkbox"])').all()
    # print(f"# fieldset: {req}")
    for r in req:
        if l := locator_exists(r, 'legend >> span[aria-hidden="true"]'):
            label = l.text_content().strip()
        else:
            print(f"error: no label for fieldset: {r}")
            continue            
        inputs = r.locator('input[type="checkbox"]').all()
        if init:
            if any((j:=i).is_checked() for i in inputs):
                defaults[label] = j.get_attribute('data-test-text-selectable-option__input')
                continue
            options = [i.get_attribute('data-test-text-selectable-option__input') for i in inputs]
            print(f"### options: {options}")
            if len(options) == 1: # single choice, click and continue
                print(f">>> option for: '{label}' is '{options}', click and continue")
                inputs[0].locator('..').locator('label').click()    # direct click on radio doesn't work
                continue    # don't add to defaults 1 option
            elif v := defaults.get(label, options):
                print(f">>> answer for: '{label}' is '{v}'")
                if any(((k:=j).get_attribute('data-test-text-selectable-option__input').lower()) == (a:=v['answer'].lower()) for j in inputs):
                    k.locator('..').locator('label').click()    # direct click on radio doesn't work
        if any((j:=i).is_checked() for i in inputs):
            defaults[label] = j.get_attribute('data-test-text-selectable-option__input')

def textarea(dialog, defaults: Defaults, init):
    req = dialog.locator('textarea[required]').all()
    # print(f"# textarea: {len(req)}")
    for r in req:
        label = r.get_attribute('aria-label').strip()
        val = r.input_value().strip()
        # print(f">>> textarea: '{label}'='{val}'")
        if init:
            if val:
                continue
            if v := defaults.get(label):
                print(f">>> answer for: '{label}' is '{v}'")
                r.fill(v['answer'])
        val = r.input_value().strip()
        if not val:
            print(f">>> textarea is empty: '{label}'")
            dialog.page.wait_for_timeout(TIMEOUT)
        else:
            defaults[label] = val

def select(dialog, defaults: Defaults, init):
    req = dialog.locator('select[required],select[aria-required="true"]').all()
    for r in req:
        label = get_label(r)
        val = r.input_value().strip()
        # hack: get a selected index from selector
        selected_index = dialog.page.eval_on_selector(f'select#{r.get_attribute("id")}', "select => select.selectedIndex")
        if init:
            if selected_index != 0:
                continue
            options = [i.get_attribute('value') for i in r.locator('option').all()[1:]]
            print(f"### options: {options}")
            if v := defaults.get(label, options):
                print(f">>> answer for: '{label}' is '{v}'")
                r.select_option(v['answer'])
        val = r.input_value().strip()
        selected_index = dialog.page.eval_on_selector(f'select#{r.get_attribute("id")}', "select => select.selectedIndex")
        if selected_index == 0:
            print(f">>> select is not complete: '{label}'")
            dialog.page.wait_for_timeout(TIMEOUT)
        else:
            defaults[label] = val

def input_text(dialog, defaults: Defaults, init):
    req = dialog.locator('input[required],input[aria-required="true"]').all()
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # print(f">>> required input: '{label}'='{val}' /// {defaults[label]}")
        if i.get_attribute('type') == "radio":  # special case for radio buttons
            pass
        else:
            if init:
                if val:
                    continue
                if v := defaults.get(label):
                    print(f">>> answer for: '{label}' is '{v}'")
                    i.fill(v['answer'])
            val = i.input_value().strip()
            if not val:
                print(f">>> required input is empty: '{label}'")
                dialog.page.wait_for_timeout(TIMEOUT)
            else:
                defaults[label] = val

def check_required(dialog, defaults: Defaults, init: bool):
    fieldset_radio(dialog, defaults, init)
    fieldset_checkbox(dialog, defaults, init)
    textarea(dialog, defaults, init)
    select(dialog, defaults, init)
    input_text(dialog, defaults, init)

def easy_apply_form(page, defaults: Defaults, progress: int) -> bool:
    # progress: -1 very first start, 0 - 1st page, 100 - last page
    print(">>> start easy apply form")
    while True:
        try:
            if loc := locator_exists(page, 'button >> span:text-is("Back")'):
                print("### back")
                loc.evaluate("(element) => element.addEventListener(\"click\", (event) => {window.back_handle_click(event.clientX, event.clientY)})")
            time_out = 1_000 if progress == -1 else TIMEOUT
            page.wait_for_timeout(time_out)
            page.wait_for_selector('div[role="dialog"]', state="visible")
            dialog = page.locator('div[role="dialog"]')
            if locator_exists(dialog, 'progress[value]'):
                current_progress = int(float(dialog.locator('progress[value]').get_attribute('value')))
                # print(f">>> progress: {current_progress} -> {progress}")
                init = progress != current_progress     # first time on page, get fields from defaults
                progress = current_progress
            else:   # don't have progress bar
                init = False
            check_required(dialog, defaults, init)
            defaults.save()
            if optional_locator(dialog, 'button >> span:text-is("Skip")', lambda x: x.click()):
                print(">>> skip")
                continue
            if optional_locator(dialog, 'button >> span:text-is("Next")', lambda x: x.click()):
                print(">>> next")
                check_required(dialog, defaults, False)
                defaults.save()
                continue
            if optional_locator(dialog, 'button >> span:text-is("Review")', lambda x: x.click()):
                print(">>> review")
                check_required(dialog, defaults, False)
                defaults.save()
                continue
            def follow_check(label): # hack: can't click, set uncheck, have to use label
                check = optional_locator(dialog, 'input[id="follow-company-checkbox"]', lambda x: x)
                if check and check.is_checked():
                    label.click()
            optional_locator(dialog, 'label[for="follow-company-checkbox"]', lambda x: follow_check(x))
            if locator_exists(dialog, 'button >> span:text-is("Submit application")'):
                print(">>> ready to submit")
                page.wait_for_timeout(30_000)  # time for review
                if optional_locator(dialog, 'button >> span:text-is("Submit application")', lambda x: x.click()):
                    print(">>> submit")
                    return True
        except Exception as ex:
            print(f"error: {ex}")
            return False
