# Selentric

Selentric is the successor to [selenext](https://github.com/Wykleph/selenext).  Selenext is great, but it's clunkier than 
it needs to be.  The overall idea is the same; create a template/model of a web site so we can separate the code that 
controls the automation, and the code that finds the web elements.  Selenium already has a `Page` object, but this expands 
on that a bit and brings a little more to the table.

In the future there will also be tools available for logging the source code of the web pages you need to automate.  Once 
you have the source files you can run them through a tool to generate `Page`/`PageTemplate`/`Locator` objects using 
unique class names, tag names, ids, names, etc.  These tools will require `BeautifulSoup4`.  They are not complete yet.  
Once it's done, I'm fairly certain it will make the process of setting up unique page templates a lot quicker, but like 
I said, it's not done yet.

## Install

This package is brand new and there is not an official way to install the package yet.  Download the .zip and install 
manually, or sync it with git.  The only dependency is the `selenium` bindings for python.

## Usage

An example script can be found in the root directory. It's named `example.py`.  There are 2 other files in the 
`example_page_templates` and `example_page_controllers` folders that contain the `PageTemplate`s and the
`Page` objects used in the example script.  Smaller versions of those examples are below:

## Example `PageTemplate`

```python
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
```

## Example `Page`

```python
from selenium.webdriver.remote.webdriver import WebDriver
from selentric import Page
from example_page_templates import wikipedia as wiki_templates


class WikipediaSearch(Page):  # Inherit from `Page`
    def __init__(self, driver: WebDriver):
        # Create a template that can evaluate the given conditions
        template: wiki_templates.WikipediaSearch = wiki_templates.WikipediaSearch(driver)

        self.search_url = 'https://en.wikipedia.org/w/index.php?search=&title=Special%3ASearch&go=Go'
        driver.get(self.search_url)
        # initialize the parent class and pass the template as input.
        super(WikipediaSearch, self).__init__(template, driver)

    def search(self, text: str):
        # Navigate to wiki search page if current url indicates we are
        # not on the search page.
        if self.search_url not in self.driver.current_url:
            self.driver.get(self.search_url)

        # Wait until the current web page matches the WikipediaSearch template
        # defined in example_page_templates folder.
        self.wait_for_match()
        # Wait until the document.readyState == 'complete'
        self.wait_until_ready()

        # Use the search_input Locator to find the search_input
        # web element using selenium and send keystrokes to the input.
        # Remember that you can treat the web elements as if they
        # already exist.  You don't need to call any functions, just
        # access them by using the name you gave to the Locator in
        # the PageTemplate
        self.search_input.clear()  # Make sure the search input box is empty
        self.search_input.send_keys(text)  # Fill in search text

        # Click the search button and wait for results to load.
        self.search_button.click()

        # Wait until web page matches WikipediaSearch template
        # and then wait until the document readyState == 'complete'
        self.wait_until_match_and_ready()

        return self.search_results
```

## Tying it all together

```python
from selenium.webdriver import Chrome
from time import sleep
from example_page_controllers import wikipedia
from selentric import Locator


def main(driver):
    # Create instance of the `Page` object from example above.
    wiki_search = wikipedia.WikipediaSearch(driver)

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

_driver = Chrome("C:/chromedriver.exe")
Locator.driver = _driver

try:
    main(_driver)
finally:
    print('Closing/Quitting web driver!')
    _driver.close()
    _driver.quit()
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
 
    This object supports page template matching with the `PageTemplate`
     
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

## `PageTemplate`
```
class PageTemplate(builtins.object):
  PageTemplate(driver: selenium.webdriver.chrome.webdriver.WebDriver = None):
 
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
     
        google_matcher = PageTemplate(driver)
        google_matcher.match_url('https://google.com/')
        google_matcher.match_title('Google')
        google_matcher.match_presence(input_locator)
     
        if google_matcher.matches():
            input_locator().send_keys('Selenium is awesome!')
     
    Note that this example is somewhat incomplete, as you wouldn't normally intermix
    the template code with the automation code.
```
### `PageTemplate` Methods:
```    
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

__getattr__(self, name: str):

    When an attribute is accessed that does not exist, we'll check to see if the
    template has a locator by the given attribute name.  If it does it will do
    all the checks to see if the element exists and return that element if it
    does exist.
 
    :param name:
    :return:

Data and other attributes defined here:

    driver: selenium.webdriver.chrome.webdriver.WebDriver = None
```

## `Page`
```
class Page(builtins.object):
 
    This object provides a multitude of helper methods that are great for your
    controller code.  You give it a `PageTemplate` and then you can do
    things like wait for the web page to match the given template matcher, or
    locate the selenium window handle that matches the given template.
     
    You can directly access attributes of the given `PageTemplate` and
    in turn, get access to all of it's `Locator` objects.  If you need to
    use a `Locator` directly, you can bypass the automatic nature of selentric
    objects by calling the `Page.locator` method.  This will give you the
    `Locator`, but no lookups in the DOM will be performed by selenium.
```
### `Page` Methods:
```
__init__(self, template_matcher: selentric.PageTemplate):

    There must be a PageTemplate for the Page object to use.

locate_window(self, timeout: int = -1):

    Locate the correct window by cycling through the window handles and
    running the `PageTemplate` to confirm the correct window
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

    Use this `Page`'s `PageTemplate` to check that the current web
    page matches the `PageTemplate`.
     
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
    defined in the PageTemplate that this object uses.
     
    Set timeout to something other than -1 or it will wait forever.
     
    :param poll_frequency:
    :param timeout:
    :return: self

wait_for_no_match(self, poll_frequency: float = 0.1, timeout: int = -1):
    Wait until the current window handle's web page DOES NOT match the
    template defined in the PageTemplate that this object uses.
 
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

    This enables the automatic access to Locators held in the PageTemplate
 
    :param name:
    :return: Locator

Static methods defined here:

randomly_wait(low: int, high: int)

    Sleep for a random amount of time between the low and high values provided.
 
    :param low:
    :param high:
    :return: None
```

