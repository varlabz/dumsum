import nodriver as uc

## phone field
## <input class=" artdeco-text-input--input" id="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4048436307-11229336700-phoneNumber-nationalNumber" required="" aria-describedby="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4048436307-11229336700-phoneNumber-nationalNumber-error" dir="auto" type="text">
## follow check box
## <input id="follow-company-checkbox" class="ember-checkbox ember-view visually-hidden" type="checkbox">
##     Submit application
## <button aria-label="Submit application" id="ember1046" class="artdeco-button artdeco-button--2 artdeco-button--primary ember-view" type="button"><!---->
##
## <input class=" artdeco-text-input--input" id="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4004933612-3461823937-numeric" required="" aria-describedby="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4004933612-3461823937-numeric-error" dir="auto" type="text">
## <input class=" artdeco-text-input--input" id="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4004933612-3461823913-numeric" required="" aria-describedby="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4004933612-3461823913-numeric-error" dir="auto" type="text">
## next
## <button aria-label="Continue to next step" id="ember665" class="artdeco-button artdeco-button--2 artdeco-button--primary ember-view" data-easy-apply-next-button="" type="button"><!---->

# optional select field
async def optional_select(page, field, callback):
    try:
        e = await (await page.select(field))
        callback(e)
        return e 
    except TimeoutError:
        pass

async def optional_find(page, field, callback):
    try:
        e = await (await page.find(field))
        callback(e)
        return e
    except TimeoutError:
        pass


async def easy_apply_form(page):
    # check empty fields if have any then stop
    req = await page.select_all('input[required]')
    print(req)
    for i in req:
        if await i.get_attribute('value') == '':
            print('empty field found')
            return
    # uncheck follow company
    optional_select(page, 'input[id="follow-company-checkbox"]', lambda x: x.click())
    if optional_find(page, 'Continue to next step', lambda x: x.click()):
        page.sleep(1)
        easy_apply_form(page)

async def if_login(page, email: str, password: str):
    try:
        await (await page.find('Sign in with email')).click()
        await page.sleep(5)

        optional_select(page, 'input[type=text]', lambda x: x.send_keys(email))
        # try: 
        #     await (await page.select("input[type=text]")).send_keys(email)
        # except TimeoutError:
        #     pass
        await (await page.select("input[type=password]")).send_keys(password)
        await (await page.select('button[type="submit"]')).click()
        await page.sleep(50)
    except TimeoutError:
        pass    

async def start():
    browser = await uc.start(
        user_data_dir="linked-in",
    )
    page = await browser.get('https://www.linkedin.com/')
    await page
    return (browser, page)

async def go_to_jobs(browser, page, keywords):
    # go to jobs page
    await browser.get('https://www.linkedin.com/jobs/')
    await page.sleep(5)
    await (await page.select('input[id^=jobs-search-box-keyword-id-]')).send_keys(keywords)
    # await (await page.select('input[id^=jobs-search-box-location-id-]')).send_keys('San Jose, California')
    await (await page.find('Search')).click()
    await page.sleep(5)
    # get list of positions, max 25 items. use 1st page only
    list = await page.select_all('ul.scaffold-layout__list-container > li.jobs-search-results__list-item')
    return list

async def main(email: str, password: str, keywords: str):
    (browser, page) = await start()
    try:
        await browser.cookies.load()
    except FileNotFoundError:
        pass
    await page.sleep(5)    
    await if_login(page, email, password)
    await browser.cookies.save()
    list = await go_to_jobs(browser, page, keywords)
    # will do easy apply only
    # TODO: make a plugin system to apply on another sites
    print(f"positions: {len(list)}")
    for i in list:
        await i.scroll_into_view()  # make element visible or will have stange None exception
        a = await i.query_selector('a.job-card-container__link')
        # print(a.attrs['href'])
        await a.click()
        # if want to not show the position again, click on cross
        c = await i.query_selector('button.job-card-container__action-small')
        await c.click()
        await page.sleep(5)
        # get easy apply
        ea = await page.query_selector('button.jobs-apply-button[data-job-id]')
        if not ea is None:      # ignore not Easy Apply positions
            await ea.click()
            await easy_apply_form(page)
            await page.sleep(500)
        await page.sleep(5)
    await page.sleep(500)

if __name__ == '__main__':
    # since asyncio.run never worked (for me)
    uc.loop().run_until_complete(main("deepblue@umdoze.com", "VeryBigPassword+1", 'android tpm'))
    # uc.loop().run_until_complete(main("jon.Wat@umdoze.com", "VeryBigP@s$word1", 'android tpm'))



