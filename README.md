# Selentric

Selentric is the successor to [selenext](https://github.com/Wykleph/selenext).  Selenext is great, but it's clunkier than 
it needs to be.  The overall idea is the same; create a template/model of a web site so we can separate the code that 
controls the automation, and the code that finds the web elements.  Selenium has a `Page` object but this expands on that
a little bit and brings a little bit more to the table.

In the future there will also be tools available for logging the source code of the web pages you need to automate.  Once 
you have the source files you can run them through a tool to generate `Page`/`PageTemplateMatcher`/`Locator` objects using 
unique class names, tag names, ids, names, etc.  These tools will require `BeautifulSoup4`.  They are not complete yet.  
Once it's done, I'm fairly certain it will make the process of setting up unique page templates a lot quicker, but like 
I said, it's not done yet.

### Install

This package is brand new and there is not an official way to install the package yet.  Download the .zip and install 
manually, or sync it with git.  The only dependency is the `selenium` bindings for python.

### Usage

The idea behind selentric is very similar to selenext.  We want to create a template, or view, for the web pages that
we are going to be working with, and the template code should not be intermingled with the code that drives the automation.
This template will hold all the information needed to locate the web elements we need to automate.  Once we have defined 
a template to use, we can give that template to the `Page` object, which provides helper functions for writing controllers
while cutting down on overly-verbose selenium code.  To do this we need to import the `PageTemplateMatcher`,`Locator`, 
`Page`, and `By` objects.  The example below is fairly comprehensive and is documented pretty well, although this example
does not show all of the available methods. It shows how to set up a custom `Page` object with a `PageTemplateMatcher`.  
The controller portion of the code is in the `if __name__ == "__main__":` block.

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

## Selentric Class Objects

The 3 class objects selentric uses are documented below.

## `Locator`
```
class Locator(builtins.object):
 
    This object stores the information needed to look up a webpage
    element using selenium's `find_element_by_*` methods.  This object
    does not locate the element until it's called like a function,
    the `find` method is called, or you try to use a method, or access
    an attribute that is on a selenium web element object.
 
    This object supports page template matching with the `PageTemplateMatcher`
     
    When an element is located successfully, a copy of the selenium
    element object is stored and you can call any of it's methods
    using this Locator object.  Access the stored web element in
    the `element` attribute, or multiple results in the `results`
    attribute.
 
    Basic Example:
        search_input = Locator(by=By.NAME, locator='q', name='search_input')
 
        # We do not have to call `find`/call the object itself.
        # As soon as you try to access a method that doesn't
        # exist on the Locator object, the Locator will try to
        # find that attribute or method on the selenium web
        # element that was stored last time it was found.  If
        # the element hasn't been found, the Locator will
        # attempt to locate the element before attempting to
        # access the attribute, or in this case, call a
        # selenium web element method.
        search_input.send_keys('ello poppet')
```

### `Locator` Methods:
```
__init__(self, by: selenium.webdriver.common.by.By = 'id', locator: str = '', name='', parent=None, multiple=False, driver=None):

    Initialize the Locator.  Store the information about how the locator should
    locate web elements.
     
    Make sure to use the `name` kwarg to set the name of the Locator if you want
    to access the Locator/web element as an attribute on the `Page` object.
     
    You can set a parent Locator with the `parent` kwarg.  Before the web element
    is located, the parent Locator will locate the parent element, then the parent
    web element will be used to locate the child element.
     
    You can also get a list of web elements that match the given Locator by setting
    the `multiple` kwarg to `True`
     
    You can pass in a web driver using the `driver` kwarg.  You can set the web
    driver for all Locators by setting `Locator.driver` as a static variable.
     
    :param by:
    :param locator:
    :param name:
    :param parent:
    :param multiple:
    :param driver:
    :return: None
    
find(self):

    Attempt to locate the web page element described by the Locator.
 
    :return: selenium.webdriver.chrome.webdriver.WebDriver | list


@staticmethod
set_driver(driver: selenium.webdriver.chrome.webdriver.WebDriver):

    Set the driver that should be used for all of the Locator instances.
 
    :param driver:
    :return:

__bool__(self):

    Check if the web element has been found when compared as a boolean.
 
    :return:
    
__call__(self, *args, **kwargs):
    
    If the class instance is called like a function, attempt to locate the web element
    described by the Locator.
     
    :return:
    
__getattr__(self, name: str):

    Called when trying to access an attribute that does not exist on the Locator object.
     
    In order to allow quick/easy access to the selenium web element's methods, we check
    if there is a web element that has already been found.  If there is no found element
    then we attempt to find it.  If we can find the web element we attempt to return
    the attribute from the web element object.
    
    :return: 
 
    This is what allows this kind of syntax:
 
        wiki_search.search_input.send_keys("selentric!")
 
    Otherwise we would have to write our code like this:
 
        wiki_search.search_input().send_keys("selentric!")
 
    or even worse, like this:
 
        wiki_search.search_input.find().send_keys("selentric!")
 
    :param name:

Data and other attributes defined here:

    driver: selenium.webdriver.chrome.webdriver.WebDriver = None
```

## `PageTemplateMatcher`
```
class PageTemplateMatcher(builtins.object):
  PageTemplateMatcher(driver: selenium.webdriver.chrome.webdriver.WebDriver = None):
 
    Use this object to verify the state of a web page by checking that
    all the given expected conditions have been met.
     
    This object lets you register `expected_conditions` that will not be
    evaluated until you run the `matches` method.  When `matches` is
    called, the each condition in the list of expected conditions will
    be evaluated.  If any of the conditions are not met then the object
    returns False, otherwise it returns True.
     
    Basic Example:
    
        driver.get('https://google.com/')
        input_locator = Locator('search-input', driver, by=By.NAME, locator='q')
     
        google_matcher = PageTemplateMatcher(driver)
        google_matcher.match_url('https://google.com/')
        google_matcher.match_title('Google')
        google_matcher.match_presence(input_locator)
     
        if google_matcher.matches():
            input_locator().send_keys('Selenium is awesome!')
     
    Note that this example is somewhat incomplete, as you wouldn't normally intermix
    the template code with the automation code.
```
### `PageTemplateMatcher` Methods:
```
__getattr__(self, name: str):

    When an attribute is accessed that does not exist, we'll check to see if the
    template has a locator by the given attribute name.  If it does it will do
    all the checks to see if the element exists and return that element if it
    does exist.
 
    :param name:
    :return:
    
__init__(self, driver=None):

    Initialize self.  See help(type(self)) for accurate signature.
    
    :return: None

add_locator(self, element: selentric.Locator):

    Tell the template matcher that it should store a locator, but won't use
    that locator for template matching.  The locator will be accessible as
    an attribute on this object using it's set name.
 
    :param element:
    :return: self
    
add_locator_by_name(self, element: selentric.Locator, name: str):

    Tell the template matcher that it should store a locator, but won't use
    that locator for template matching.  The locator will be accessible as
    an attribute on this object using the name provided in the method call.
 
    :param element:
    :param name:
    :return: self
    
match_alert_present(self):

    Tell the template matcher that an alert box should be open on the screen.
 
    :return: self
    
match_clickable_element(self, element: selentric.Locator):

    Tell the template matcher it should be able to find a web page
    element with the given `Locator`, and that the element is also
    clickable by the user.
     
    :param element:
    :return: self

match_element_text(self, element: selentric.Locator, text: str):

    Tell the template matcher it should be able to find a web page
    element with the given `Locator`, and that the text matches
    the given text.
     
    :param element:
    :param text:
    :return: self
    
match_element_value_text(self, element: selentric.Locator, text: str):

    Tell the template matcher it should be able to find a web page
    element with the given `Locator`, and that the text in the
    `value` attribute of the web page element it finds, matches
    the given text.
     
    :param element:
    :param text:
    :return: self
    
match_invisibility(self, element: selentric.Locator):

    Tell the template matcher it should NOT be able to find a web
    page element with the given Locator, or that web page element
    is invisible to the user.
     
    :param element:
    :return: self
    
match_partial_title(self, text: str):
    Tell the template matcher that the title of the web page
    should contain the given text.
     
    :param text:
    :return: self
    
match_partial_url(self, text: str):

    Tell the template matcher it should contain the given text in the
    current URL.
     
    :param text:
    :return: self
    
match_presence(self, element: selentric.Locator):

    Tell the template matcher it should be able to find a web page
    element with the given `Locator`.
     
    :param element:
    :return: self
    
match_title(self, title: str):

    Tell the template matcher that the title of the web page
    should match the given text.
     
    :param title:
    :return: self
    
match_url(self, url: str):

    Tell the template matcher it should match the given URL with the current
    URL in the web driver.
     
    :param url:
    :return: self
    
match_visibility(self, element: selentric.Locator):

    Tell the template matcher it should be able to find a web page
    element with the given `Locator`, and that it should be visible
    on the page.
     
    :param element:
    :return: self
    
matches(self, timeout: float = 0.01, debug: bool = False, poll_frequency: float = 0.1):
    
    Perform the template match and return True/False if the template
    matches what was defined prior to calling this method.
     
    This method reads the `self.expected_conditions` list and tries
    to very that the expected conditions have been met.  If any of
    the expected conditions fails then the method returns False.
    If all expected conditions are met, the method returns True.
     
    :param timeout:
    :param debug:
    :param poll_frequency:
    :return: bool
    
set_driver(self, driver: selenium.webdriver.chrome.webdriver.WebDriver):

    Set the driver as a static attribute so that all PageTemplateMatchers use the same
    web driver instance.
     
    :param driver:
    :return: self

Data and other attributes defined here:

    driver: selenium.webdriver.chrome.webdriver.WebDriver = None
```

## `Page`
```
class Page(builtins.object):
 
    This object provides a multitude of helper methods that are great for your
    controller code.  You give it a `PageTemplateMatcher` and then you can do
    things like wait for the web page to match the given template matcher, or
    locate the selenium window handle that matches the given template.
     
    You can directly access attributes of the given `PageTemplateMatcher` and
    in turn, get access to all of it's `Locator` objects.  If you need to
    use a `Locator` directly, you can bypass the automatic nature of selentric
    objects by calling the `Page.locator` method.  This will give you the
    `Locator`, but no lookups in the DOM will be performed by selenium.
```
### `Page` Methods:
```
__init__(self, template_matcher: selentric.PageTemplateMatcher):

    There must be a PageTemplateMatcher for the Page object to use.

locate_window(self, timeout: int = -1):

    Locate the correct window by cycling through the window handles and
    running the `PageTemplateMatcher` to confirm the correct window
    handle is currently selected.
     
    Set `timeout` to something other than -1 if you don't want it
    to attempt to locate the window forever.
     
    :param timeout:
    :return: None

locator(self, locator_name: str):
    
    Get the `Locator` instance using the `Locator`'s lookup name, without
    calling `find` or trying to find the web element.
     
    :param locator_name:
    :return: Locator

matches(self, debug: bool = False, timeout: float = 0.01):

    Use this `Page`'s `PageTemplateMatcher` to check that the current web
    page matches the `PageTemplateMatcher`.
     
    :param debug:
    :param timeout:
    :return: bool

wait_for(self, element: selentric.Locator, expected_condition, timeout: int = 5, poll_frequency: float = 0.1):
    
    Wait for an element to match an expected condition.  This method is "under construction".
    Selenium already provides an api to code to for creating custom expected conditions,
    so it's probably better to create custom expected conditions for common scenarios
    and add them to the template matcher, etc.
     
    :param element:
    :param expected_condition:
    :param timeout:
    :param poll_frequency:
    :return: self

wait_for_match(self, poll_frequency: float = 0.1, timeout: int = -1):
    Wait until the current window handle's web page matches the template
    defined in the PageTemplateMatcher that this object uses.
     
    Set timeout to something other than -1 or it will wait forever.
     
    :param poll_frequency:
    :param timeout:
    :return: self

wait_for_no_match(self, poll_frequency: float = 0.1, timeout: int = -1):
    Wait until the current window handle's web page DOES NOT match the
    template defined in the PageTemplateMatcher that this object uses.
 
    Set timeout to something other than -1 or it will wait forever.
     
    :param poll_frequency:
    :param timeout:
    :return: self

wait_until_ready(self, timeout: int = 60, poll_frequency: float = 0.5):

    Wait until the document readyState == complete

    :param timeout:
    :param poll_frequency:
    :return: self

__getattr__(self, name: str):

    This enables the automatic access to Locators held in the PageTemplateMatcher
 
    :param name:
    :return: Locator

Static methods defined here:

randomly_wait(low: int, high: int)

    Sleep for a random amount of time between the low and high values provided.
 
    :param low:
    :param high:
    :return: None
```

