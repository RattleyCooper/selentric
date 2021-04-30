from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from page_templates import wikipedia
from automation import Locator


def main(driver):
    wiki_search = wikipedia.WikipediaSearch(driver)
    wiki_login = wikipedia.WikipediaSignIn(driver)

    driver.get('https://en.wikipedia.org/w/index.php?search=&title=Special%3ASearch&go=Go')

    wiki_search.wait_for_match()
    wiki_search.wait_until_ready()
    wiki_search.search_input.send_keys('Selentric')
    wiki_search.search_button.click()

    wiki_login.wait_for_match()
    wiki_login.wait_until_ready()
    wiki_login.username_input.send_keys('doodoobutt')
    wiki_login.password_input.send_keys('teeheehee')


    sleep(6)


# Set the web driver that all `Locator` objects use
# to drive the browser.  This will take place across
# all Locator instances.
_driver = Chrome("C:/chromedriver.exe")
Locator.set_driver(_driver)

try:
    main(Locator.driver)
finally:
    print('Closing/Quitting web driver!')
    Locator.driver.close()
    Locator.driver.quit()
