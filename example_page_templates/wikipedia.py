from selentric import PageTemplate, Locator, By


class WikipediaSearch(PageTemplate):
    def __init__(self, driver):
        super(WikipediaSearch, self).__init__(driver)
        
        # Define conditions that must be met.

        # Part of the URL will contain the given text
        self.match_partial_url('wikipedia.org/w/index.php?search=')
        # The title will match the given text exactly
        self.match_partial_title('Search')

        # A web element is present with a name attribute matching "search".  This web element
        # can be accessed with the "search_input" attribute on the `Page` object.
        self.match_presence(Locator(By.NAME, 'search', name='search_input'))
        # A web element is present with a class name attribute matching "oo-ui-actionFieldLayout-button".
        # This web element can be accessed with the "search_button" attribute on the `Page` object.
        self.match_presence(
            Locator(By.CLASS_NAME, 'oo-ui-actionFieldLayout-button', name='search_button')
        )
        # A web element is present with a class name attribute matching "mw-advancedSearch-container".
        # This web element is not interacted with by our script, so we don't need to give it a name.
        self.match_presence(Locator(By.CLASS_NAME, 'mw-advancedSearch-container'))

        # Add a locator that can still be accessed with the `Page` object, but don't use it for template matching.
        self.add_locator(Locator(By.ID, 'pt-login', name='login_link'))

        # Create Locator to use as a parent Locator so we can get search results
        results_list_element = Locator(By.CLASS_NAME, 'mw-search-results')
        # Use `parent` and `multiple` kwargs. The parent is found first
        # and the resulting web element is used to find the child Locator.
        # The multiple kwarg will make the locator find multiple web elements
        # if they exist and a list of web elements is returned instead of a
        # single web element.
        self.add_locator(
            Locator(By.TAG_NAME, 'li', name='search_results', parent=results_list_element, multiple=True)
        )


class WikipediaSignIn(PageTemplate):
    def __init__(self, driver):
        super(WikipediaSignIn, self).__init__(driver)
        
        self.match_partial_url('Special:UserLogin')
        self.match_title('Log in - Wikipedia')

        self.match_presence(Locator(By.NAME, 'wpName', name='username_input'))
        self.match_presence(Locator(By.NAME, 'wpPassword', name='password_input'))
        self.match_presence(Locator(By.NAME, 'wploginattempt', name='login_button'))

