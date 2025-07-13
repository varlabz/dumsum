import argparse
from operator import itemgetter
import os
import threading

def set_interval(callback, seconds, *args, **kwargs):
    """
    Calls the callback every `seconds`.
    Returns a function to cancel the timer.
    """
    stopped = threading.Event()

    def loop():
        while not stopped.wait(seconds):
            callback(*args, **kwargs)

    thread = threading.Thread(target=loop)
    thread.daemon = True
    thread.start()
    return stopped.set

def delay_call(page, callback, delay=5_000):
    page.wait_for_timeout(delay)
    callback()

def locator_exists(page, selector, **kargs):
    return (loc := page.locator(selector, **kargs)).count() > 0 and loc

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
    if (t := el.locator('..').locator('label')).count() > 0:
        el = t
    elif (t := el.locator('..').locator('..').locator('label')).count() > 0: # sometimes need to check 1 level up
        el = t
    return remove2(' '.join(el.text_content().split()))

def get_data_file(file: str):
    if os.path.exists(f := f"data/{file}"):
        return f
    if os.path.exists(file):
        return file
    raise Exception(f"File not found: {file}")

def config():
    parser = argparse.ArgumentParser(description="LinkedIn Bot")
    parser.add_argument("--url", default=None, type=str, required=False, help="URL to process")
    parser.add_argument("--matcher", default=70, type=int, required=False, help="Use resume matcher to filter job positions (default 70). Specify a percentage (0-100) for matching threshold.")
    parser.add_argument("--matcher-ignore", default=60, type=int, required=False, help="Use resume matcher to mark as ignore (default 60). Specify a percentage (0-100) for matching threshold.")
    parser.add_argument("--speed", type=int, required=False, default=1, help="Speed of the process. 0 - slow(default), 1 - fast")
    parser.add_argument("--click-apply", action='store_true', default=True, required=False, help="Click to 'Apply' button")
    parser.add_argument("--click-easy-apply", action='store_true', default=True, required=False, help="Click to 'Easy Apply' button")
    parser.add_argument("--max-pages", type=int, required=False, default=1000, help="Max pages to process. default 1000")
    parser.add_argument("--debug-easy-apply-form", action='store_true', default=False, required=False, help="Debug: use 'easy apply' form to current position only")
    parser.add_argument("--debug-matcher", action='store_true', default=False, required=False, help="Debug: show match value only")
    parser.add_argument("--debug-1page", action='store_true', default=False, required=False, help="Debug: run 1 page only and apply to 'easy apply' position")
    parser.add_argument("--debug-no-url", action='store_true', default=False, required=False, help="Debug: do not use URL file")
    args = parser.parse_args()
    return args
