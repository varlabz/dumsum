import yaml
from chat import answer
from common import *


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
    # print(f"# input required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # print(f">>> required input: '{label}'='{val}' /// {defaults.get(label, None)}")
        if i.get_attribute('type') == "radio":  # special case for radio buttons
            #check_radio(i) # TODO do it right way. use label and radio buttons as values
            pass
        else:
            if init:
                if val:
                    continue
                if defaults.get(label, None):
                    i.fill(str(defaults[label]))
                    continue              
                res = answer(label)   
                print(f">>> answer for: '{label}' is '{res}'")
                if res: # answer can be 0, accept it
                    i.fill(str(res['answer']))
            else:
                if not val:
                    print(f">>> required input is empty: '{label}'")
                    page.wait_for_timeout(5_000)
                else:
                    defaults[label] = val

    req = dialog.locator('select[required],select[aria-required="true"]').all()
    # print(f"# select required: {len(req)}")
    for i in req:
        label = get_label(i)
        val = i.input_value().strip()
        # hack: get a selected index from selector
        selected_index = page.eval_on_selector(f'select#{i.get_attribute("id")}', "select => select.selectedIndex")
        # print(f">>> required select: '{label}'='{val}':{selected_index}///{defaults.get(label, None)}")
        if init:
            if selected_index != 0:
                continue
            if defaults.get(label, None):
                i.select_option(defaults[label])
                continue
            res = answer(label)   
            print(f">>> answer for: '{label}' is '{res}'")
            if res and res['answer']:
                try:
                    i.select_option(res['answer'])
                except Exception as ex:
                    print(f"error: {ex}")
        else:
            if selected_index == 0:
                page.wait_for_timeout(5_000)
            else:
                defaults[label] = val

DEFAULTS = "data/defaults.yaml"

def save_defaults(defaults: dict):
    with open(DEFAULTS, "w") as file:
        yaml.dump(defaults, file, width=float('inf'), default_flow_style=False, sort_keys=False)

def easy_apply_form(page, defaults: dict, progress: int) -> bool:
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
                page.wait_for_timeout(30_000)
                if optional_locator(dialog, 'button >> span:text-is("Submit application")', lambda x: x.click()):
                    print(">>> submit")
                    return True

        except Exception as ex:
            print(f"error: {ex}")
            return False

