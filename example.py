from selenium.webdriver import Chrome
from time import sleep
from example_page_controllers import wikipedia
from selentric import Locator


def main(driver):
    wiki_search = wikipedia.WikipediaSearch(driver)
    wiki_login = wikipedia.WikipediaSignIn(driver)

    # Search for Red Pandas
    red_panda_results = wiki_search.search("Red Panda")
    # Go through the list of red panda results and print the text
    # from the selenium web element.
    for red_panda_result in red_panda_results:
        print(red_panda_result.text)
    sleep(5)

    # Search for Tree Frogs
    tree_frog_results = wiki_search.search("Tree Frog")
    for tree_frog_result in tree_frog_results:
        print(tree_frog_result.text)
    sleep(5)

    wiki_login.sign_in('bobabooeybobabooey', 'not-a-real-password', testing=True)
    sleep(5)


_driver = Chrome("C:/chromedriver.exe")
Locator.driver = _driver

try:
    main(_driver)
finally:
    print('Closing/Quitting web driver!')
    _driver.close()
    _driver.quit()
