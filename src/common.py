def delay_call(page, callback, delay=5_000):
    page.wait_for_timeout(delay)
    callback()

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
