from selentric import PageTemplateMatcher, Locator, Page, By


class WikipediaSearch(Page):  # Inherit from `Page`
    def __init__(self, driver):
        # Create a template that can evaluate the given conditions
        template: PageTemplateMatcher = PageTemplateMatcher(driver)

        # Define conditions that must be met.

        # Part of the URL will contain the given text
        template.match_partial_url('wikipedia.org/w/index.php?search=')
        # The title will match the given text exactly
        template.match_title('Search - Wikipedia')

        # A web element is present with a name attribute matching "search".  This web element
        # can be accessed with the "search_input" attribute on the `Page` object.
        template.match_presence(Locator(By.NAME, 'search', name='search_input'))
        # A web element is present with a class name attribute matching "oo-ui-actionFieldLayout-button".
        # This web element can be accessed with the "search_button" attribute on the `Page` object.
        template.match_presence(
            Locator(By.CLASS_NAME, 'oo-ui-actionFieldLayout-button', name='search_button')
        )
        # A web element is present with a class name attribute matching "mw-advancedSearch-container".
        # This web element is not interacted with by our script, so we don't need to give it a name.
        template.match_presence(Locator(By.CLASS_NAME, 'mw-advancedSearch-container'))

        # Add a locator that can still be accessed with the `Page` object, but don't use it for template matching,
        template.add_locator(Locator(By.ID, 'pt-login', name='login_link'))

        # initialize the parent class and pass the template as input.
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
