import yaml
from chat import answer
from common import *
from defaults import Defaults

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
            if v := defaults[label]:
                print(f">>> answer for: '{label}' is '{v}'")
                print(f"### options: {[i.get_attribute('data-test-text-selectable-option__input') for i in inputs]}")
                if any(((k:=j).get_attribute('data-test-text-selectable-option__input').lower()) == (a:=v['answer'].lower()) for j in inputs):
                    k.locator('..').locator('label').click()    # direct click on radio doesn't work
        else:
            if any((j:=i).is_checked() for i in inputs):
                defaults[label] = j.get_attribute('data-test-text-selectable-option__input')
                continue

def textarea(dialog, defaults: Defaults, init):
    req = dialog.locator('textarea[required]').all()
    # print(f"# textarea: {len(req)}")
    for r in req:
        label = r.get_attribute['aria-label'].strip()
        print(label)
        val = r.input_value().strip()
        print(f">>> textarea: '{label}'='{val}'///{defaults[label]}")
        if init:
            if val:
                continue
            if v := defaults.get(label):
                print(f">>> answer for: '{label}' is '{v}'")
                r.fill(v['answer'])
                continue
        else:
            if not val:
                print(f">>> textarea is empty: '{label}'")
            else:
                defaults[label] = val

def check_required(page, dialog, defaults: Defaults, init):
    fieldset_radio(dialog, defaults, init)
    textarea(dialog, defaults, init)
    # check empty fields
    req = dialog.locator('input[required],input[aria-required="true"]').all()
    # print(f"# input required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # print(f">>> required input: '{label}'='{val}' /// {defaults[label]}")
        if i.get_attribute('type') == "radio":  # special case for radio buttons
            # check_radio(i) # TODO do it right way. use label and radio buttons as values
            pass
        else:
            if init:
                if val:
                    continue
                if v := defaults.get(label):
                    print(f">>> answer for: '{label}' is '{v}'")
                    i.fill(v['answer'])
                    continue              
            else:
                if not val:
                    print(f">>> required input is empty: '{label}'")
                    page.wait_for_timeout(10_000)
                else:
                    defaults[label] = val

    req = dialog.locator('select[required],select[aria-required="true"]').all()
    # print(f"# select required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # hack: get a selected index from selector
        selected_index = page.eval_on_selector(f'select#{i.get_attribute("id")}', "select => select.selectedIndex")
        # print(f">>> required select: '{label}'='{val}':{selected_index}///{defaults[label]}")
        if init:
            if selected_index != 0:
                continue
            if v := defaults.get(label):
                print(f">>> answer for: '{label}' is '{v}'")
                i.select_option(v['answer'])
                continue
        else:
            if selected_index == 0:
                page.wait_for_timeout(10_000)
            else:
                defaults[label] = val

def easy_apply_form(page, defaults: Defaults, progress: int) -> bool:
    # progress: -1 very first start, 0 - 1st page, 100 - last page
    # click easy apply button
    print(">>> start easy apply form")
    while True:
        try:
            page.wait_for_timeout(15_000)
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
            defaults.save()

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
                page.wait_for_timeout(30_000)
                if optional_locator(dialog, 'button >> span:text-is("Submit application")', lambda x: x.click()):
                    print(">>> submit")
                    return True

        except Exception as ex:
            print(f"error: {ex}")
            return False

