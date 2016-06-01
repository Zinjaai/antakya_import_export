from splinter import Browser

BASE_URL = 'http://217.86.233.218/FoodCoop/'
FOOD_COOP_ID = 'FILL IN HERE!'
LOGIN_NAME = 'FILL IN HERE!'
PASSWORD = 'FILL IN HERE!'


class AntakyaConnection:
    def __enter__(self):
        browser = Browser()
        url = BASE_URL + 'login.jsp'
        browser.visit(url)
        with browser.get_iframe('base'):
            browser.fill('loginfoodcoopid', FOOD_COOP_ID)
            browser.fill('loginnickname', LOGIN_NAME)
            browser.fill('loginpassword', PASSWORD)
            browser.find_by_name('').first.click()
            return browser

    def __exit__(self, type, value, traceback):
        pass
