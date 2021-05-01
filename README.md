# Selentric

Selentric is the successor to [selenext](https://github.com/Wykleph/selenext).  Selenext is great, but it's clunkier than 
it needs to be.  The overall idea is the same; create a template/model of a web site so we can separate the code that 
controls the automation, and the code that finds the web elements.

There will also be tools available for logging the source code of the web pages you need to automate.  Once you have the
source files you can run them through a tool to generate `Page`/`PageTemplateMatcher`/`Locator` objects using unique 
class names, tag names, ids, names, etc.  These tools will require `BeautifulSoup4`.

### Install

This package is brand new and there is not an official way to install the package yet.  Download the .zip and install 
manually.  The only dependency is the `selenium` bindings for python.

### Usage

The idea behind selentric is very similar to selenext.  We want to create a template, or view, for the web pages that
we are going to be working with, and the template code should not be intermingled with the code that drives the automation.
This template will hold all the information needed to locate the web elements we need to automate.  Once we have defined 
a template to use, we can give that template to the `Page` object, which provides helper functions for writing controllers
while cutting down on overly-verbose selenium code.  To do this we need to import the `PageTemplateMatcher`,`Locator`, 
`Page`, and `By` objects.  The example below is fairly comprehensive and is documented pretty well, although it does not
show all of the available methods. It shows how to set up a custom `Page` object with a `PageTemplateMatcher`.  The 
controller portion of the code is in the `if __name__ == "__main__":` block.

```python
# Selentric imports `By` from selenium, so it's the same object.
from selentric import PageTemplateMatcher, Locator, Page, By


class WikipediaSearch(Page):
    """
    Inherit from `Page` to create custom page object.
    Each unique web page or page state should have its
    own custom `Page` class.  This will be used to detect
    that a specific state has been reached, and can also
    automatically locate the selenium window handle that
    matches the given `Page`'s `PageTemplateMatcher`.
    """

    def __init__(self, driver):  # Pass in a selenium web driver to initialize
        # Create a template that can evaluate the given conditions
        # We don't pass the template to this class because the
        # idea behind selentric is to separate template code from
        # controller code. The separation of concerns makes things
        # easy to maintain/update.
        template: PageTemplateMatcher = PageTemplateMatcher(driver)

        # Define conditions that must be met using `match_*` methods.
        # The `match_*` methods tell the template matcher how the
        # web page needs to appear, or which elements need to be
        # present, missing, etc.

        # Part of the URL will contain the given text
        template.match_partial_url('wikipedia.org/w/index.php?search=')
        # template.match_url('https://wikipedia.org/') <- must match title exactly

        # The title will match the given text exactly
        template.match_title('Search - Wikipedia')
        # template.match_partial_title('Search') <- no need to match exact title

        # When you tell a template matcher to match a condition
        # that requires a `Locator`, it will automatically set
        # the `name` given to the `Locator` as an attribute
        # on the template matcher.  These are also accessible
        # through the `Page` object as attributes.  It is important
        # to name the `Locator`s you need to interact with.
        # The next line of code shows the use of a named `Locator`.

        # A web element is present with a name attribute matching "search".
        # This web element can be accessed with the "search_input" attribute
        # on the `Page` object.
        template.match_presence(Locator(By.NAME, 'search', name='search_input'))

        # A web element with a name attribute matching "bobabooey" is
        # not present in the DOM, or it is invisible to the user.
        # Note that no `name` kwarg is given because we don't need to
        # access this `Locator` through the `Page` object.
        template.match_invisibility(Locator(By.NAME, 'bobabooey'))

        # A web element is present with a class name attribute matching
        # "oo-ui-actionFieldLayout-button".  This web element can be
        # accessed with the "search_button" attribute on the `Page` object.
        template.match_presence(
            Locator(By.CLASS_NAME, 'oo-ui-actionFieldLayout-button', name='search_button')
        )
        # A web element is present with a class name attribute matching
        # "mw-advancedSearch-container".  This web element is not
        # interacted with by our script, so we don't need to give
        # it a name.
        template.match_presence(Locator(By.CLASS_NAME, 'mw-advancedSearch-container'))

        # Add a locator that can be accessed with the `Page` object,
        # but it will not be used for any template matching.
        template.add_locator(Locator(By.ID, 'pt-login', name='login_link'))

        # initialize the parent class and pass the template as input.
        super(WikipediaSearch, self).__init__(template)


if __name__ == '__main__':
    from selenium.webdriver import Chrome

    def main(driver):

        # Assign driver to all Locator instances
        Locator.driver = driver
        # Create our Page object.
        wiki_search = WikipediaSearch(driver)

        # Go to the wiki search page.
        driver.get('https://en.wikipedia.org/w/index.php?search=&title=Special%3ASearch&go=Go')

        # Wait until the current web page matches the wiki search template defined above
        wiki_search.wait_for_match()

        # If your web page opens in a new window, you can use the `locate_window` method.
        # This cycles through all the window handles and switches to the window handle that
        # matches the template.  This would be used instead of `wait_for_match`.
        wiki_search.locate_window()

        # Wait until the document.readyState == 'complete'.
        wiki_search.wait_until_ready()

        # Interact with the named Locators using our `Page` object.
        wiki_search.search_input.send_keys('Selentric')
        wiki_search.search_button.click()

        # Wait until the page no longer matches the WikiSearch page template
        wiki_search.wait_for_no_match(timeout=5)


    # Create driver and start main function.
    chrome_driver = Chrome()
    try:
        main(chrome_driver)
    finally:
        print('Closing/Quitting driver.')
        chrome_driver.close()
        chrome_driver.quit()
```

### Full Documentation Soon


