from selenium.webdriver.common.by import By
from automation import PageTemplateMatcher, Locator, Page


class WikipediaSearch(Page):
    def __init__(self, driver):
        template: PageTemplateMatcher = PageTemplateMatcher(driver)

        template.match_partial_url('wikipedia.org/w/index.php?search=')
        template.match_title('Search - Wikipedia')

        template.match_presence(Locator(By.NAME, 'search', name='search_input'))
        template.match_presence(
            Locator(By.CLASS_NAME, 'oo-ui-actionFieldLayout-button', name='search_button')
        )
        template.match_presence(Locator(By.CLASS_NAME, 'mw-advancedSearch-container', name='adv_search_cont'))

        template.add_locator(Locator(By.ID, 'pt-login', name='login_link'))

        super(WikipediaSearch, self).__init__(template)


class WikipediaSignIn(Page):
    def __init__(self, driver):
        template = PageTemplateMatcher(driver)

        template.match_partial_url('Special:UserLogin')
        template.match_title('Log in - Wikipedia')

        template.match_presence(Locator(By.NAME, 'wpName', name='username_input'))
        template.match_presence(Locator(By.NAME, 'wpPassword', name='password_input'))
        template.match_presence(Locator(By.NAME, 'wploginattempt', name='login_button'))

        super(WikipediaSignIn, self).__init__(template)
