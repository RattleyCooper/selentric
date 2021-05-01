# Selentric

Selentric is the successor to [selenext](https://github.com/Wykleph/selenext).  Selenext is great, but
it's clunkier than it needs to be.  I haven't looked at selenext for a long while and I decided to start
a whole new project as I am getting back into a heavy web automation projects and need to get things up and 
running faster than selenext allows.

### Install

This package is brand new and there is not an official way to install the package yet.  Download the .zip and install 
manually.  The only dependency is the `selenium` bindings for python.

### Usage

The idea behind selentric is very similar to selenext.  We want to create a template, or view, for the web pages that
we are going to be working with.  This template will hold all the information needed to locate the web elements we need
to automate.  Once we have defined a template to use, we can give that template to the `Page` object, which provides
helper functions to make writing automation code dead simple.  To do this we need to import the `PageTemplateMatcher`, 
`Locator`, `Page`, and `By` objects.

```python
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


if __name__ == '__main__':
    from selenium.webdriver import Chrome
    
    driver = Chrome()
    wiki_search = WikipediaSearch(driver)
    
    driver.get('https://en.wikipedia.org/w/index.php?search=&title=Special%3ASearch&go=Go')
    
    # Wait until the current web page matches the wiki search template
    wiki_search.wait_for_match()

    # If your web page opens in a new window, you can use the `locate_window` method.
    # This cycles through all the window handles and switches to the window handle that
    # matches the template.  This would be used instead of `wait_for_match`.
    wiki_search.locate_window()
    
    # Wait until the document.readyState == 'complete'.
    wiki_search.wait_until_ready()
    wiki_search.search_input.send_keys('Selentric')
    wiki_search.search_button.click()
    wiki_search.wait_for_no_match()
```

This documentation will be updated very soon!

