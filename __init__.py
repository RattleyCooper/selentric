from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import uuid
from time import sleep, time
import random


class Locator(object):
    """
    This object stores the information needed to look up a webpage
    element using selenium's `find_element_by_*` methods.  This object
    does not locate the element until it's called like a function,
    the `find` method is called, or you try to use a method, or access
    an attribute that is on a selenium web element object.

    This object supports page template matching with the `PageTemplateMatcher`

    When an element is located successfully, a copy of the selenium
    element object is stored and you can call any of it's methods
    using this Locator object.

    Basic Example:
        search_input = Locator(by=By.NAME, locator='q', name='search-input')

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
    """
    driver = None

    def __init__(self, by: By = By.ID, locator: str = '', name='', parent=None, multiple=False):
        self.name = name
        self.element = None
        self.found = False
        self.by = by
        self.locator = locator
        self.parent = parent
        self.multiple = multiple
        self.results = []

    def __getattr__(self, name):
        if self.element is None:
            result = self.find()
            if result is None:
                raise NoSuchElementException(f"{self.name} unable to locate element by {self.by}, with locator '{self.locator}'")
        return getattr(self.element, name)

    def __call__(self, *args, **kwargs):
        return self.find()

    def __bool__(self):
        return self.found

    @staticmethod
    def set_driver(driver):
        """
        Set the driver that should be used for all of the Locator instances.

        :param driver:
        :return:
        """
        Locator.driver = driver

    def find(self):
        """
        Attempt to locate the web page element.

        :return:
        """
        if self.parent is not None:
            parent = self.parent()
            if not self.multiple:
                result = parent.find_element(self.by, self.locator)
            else:
                result = parent.find_elements(self.by, self.locator)
                self.results = result
        else:
            if not self.multiple:
                result = Locator.driver.find_element(self.by, self.locator)
            else:
                result = Locator.driver.find_elements(self.by, self.locator)
                self.results = result

        self.element = result if result else None
        self.found = True if self.element else False
        return self.element


class url_matches(object):
    """
    This is a custom `expected_condition` for selenium's `WebDriverWait`
    object that allows you to wait until a URL matches the
    `driver.current_url`.

    Returns a copy of the webdriver used in the `WebDriverWait` object
    on success and False if unsuccessful.
    """
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        result = driver.current_url == self.url
        return driver if result else False


class url_contains(object):
    """
    This is a custom `expected_condition` for selenium's `WebDriverWait`
    object that allows you to wait until the `driver.current_url`
    contains specific text.

    Returns a copy of the webdriver used in the `WebDriverWait` object
    on success and False if unsuccessful.
    """
    def __init__(self, text):
        self.text = text

    def __call__(self, driver):

        result = self.text in driver.current_url
        return driver if result else False


class PageTemplateMatcher(object):
    """
    Use this object to verify the state of a web page by checking that
    all the given expected conditions have been met.

    This object lets you register `expected_conditions` that will not be
    evaluated until you run the `matches` method.  When `matches` is
    called, the each condition in the list of expected conditions will
    be evaluated.  If any of the conditions are not met then the object
    returns False, otherwise it returns True.

    Example:
        driver.get('https://google.com/')
        input_locator = Locator('search-input', driver, by=By.NAME, locator='q')

        google_matcher = PageTemplateMatcher(driver)
        google_matcher.match_url('https://google.com/')
        google_matcher.match_title('Google')
        google_matcher.match_presence(input_locator)

        if google_matcher.matches():
            input_locator().send_keys('Selenium is awesome!')
    """
    def __init__(self, driver=None):
        self.driver = driver
        self.expected_conditions = []
        self.locators = {}

    def set_driver(self, driver):
        self.driver = driver

    def __getattr__(self, name):
        if name not in self.locators:
            raise AttributeError(f'No attribute "{name}" exists on object and no key of "{name}" exists in locator dictionary.')
        if self.locators[name].element is None or not self.locators[name]:
            result = self.locators[name].find()
            if result is None:
                raise NoSuchElementException(f"{self.locators[name].name} unable to locate element by {self.locators[name].by}, with locator '{self.locators[name].locator}'")
        return self.locators[name].element

    def match_url(self, url: str):
        """
        Tell the template matcher it should match the given URL
        with the current URL.

        :param url:
        :return:
        """
        self.expected_conditions.append((EC.url_matches, [(url)]))
        return self

    def match_partial_url(self, text: str):
        """
        Tell the template matcher it should contain the given text in the
        current URL.

        :param text:
        :return:
        """
        self.expected_conditions.append((EC.url_contains, [(text)]))
        return self

    def _set_locator(self, element: Locator):
        new_id = uuid.uuid4().hex
        element_name = element.name if element.name else new_id
        setattr(self, element_name, element)
        self.locators[element_name] = element

    def match_presence(self, element: Locator):
        """
        Tell the template matcher it should be able to find a web page
        element with the given `Locator`

        :param element:
        :return:
        """
        self._set_locator(element)
        self.expected_conditions.append((EC.presence_of_element_located, [(element.by, element.locator)]))
        return self

    def match_visibility(self, element: Locator):
        """
        Tell the template matcher it should be able to find a web page
        element with the given `Locator`, and that it should be visible
        on the page.

        :param element:
        :return:
        """
        self._set_locator(element)
        self.expected_conditions.append((EC.visibility_of_element_located, [(element.by, element.locator)]))
        return self

    def match_invisibility(self, element: Locator):
        self._set_locator(element)
        self.expected_conditions.append((EC.invisibility_of_element_located, [(element.by, element.locator)]))
        return self

    def match_title(self, title):
        """
        Tell the template matcher that the title of the web page
        should match the given text.

        :param title:
        :return:
        """
        self.expected_conditions.append((EC.title_is, [title]))
        return self

    def match_partial_title(self, text):
        """
        Tell the template matcher that the title of the web page
        should contain the given text.

        :param text:
        :return:
        """
        self.expected_conditions.append((EC.title_contains, [text]))
        return self

    def match_element_text(self, element: Locator, text):
        """
        Tell the template matcher it should be able to find a web page
        element with the given `Locator`, and that the text matches
        the given text.

        :param element:
        :param text:
        :return:
        """
        self._set_locator(element)
        self.expected_conditions.append((EC.text_to_be_present_in_element, [(element.by, element.locator), text]))
        return self

    def match_element_value_text(self, element: Locator, text):
        """
        Tell the template matcher it should be able to find a web page
        element with the given `Locator`, and that the text in the
        `value` attribute of the web page element it finds, matches
        the given text.

        :param element:
        :param text:
        :return:
        """
        self._set_locator(element)
        self.expected_conditions.append((EC.text_to_be_present_in_element_value, [(element.by, element.locator), text]))
        return self

    def match_clickable_element(self, element: Locator):
        """
        Tell the template matcher it should be able to find a web page
        element with the given `Locator`, and that the element is also
        clickable by the user.

        :param element:
        :return:
        """
        self._set_locator(element)
        self.expected_conditions.append((EC.element_to_be_clickable, [(element.by, element.locator)]))
        return self

    def match_alert_present(self):
        self.expected_conditions.append((EC.alert_is_present, []))
        return self

    def add_locator(self, element: Locator):
        self._set_locator(element)
        return self

    def add_locator_by_name(self, element: Locator, name: str):
        setattr(self, name, element)
        element.name = name
        self.locators[name] = element

    def matches(self, timeout=.01, debug=False, poll_frequency=.1):
        """
        Perform the template match and return True/False if the template
        matches what was defined prior to calling this method.

        This method reads the `self.expected_conditions` list and tries
        to very that the expected conditions have been met.  If any of
        the expected conditions fails then the method returns False.
        If all expected conditions are met, the method returns True.

        :param timeout:
        :return:
        """

        for wait in self.expected_conditions:
            try:
                expected_condition = wait[0]
                args = wait[1]
                el = WebDriverWait(self.driver, timeout if timeout else 0.01, poll_frequency).until(
                    expected_condition(*args)
                )
            except TimeoutException:
                if debug: print(f'Timeout: Unable to locate element {wait}')
                return False
            if not el:
                if debug: print(f'Unable to locate element {wait}')
                return False
        return True


class Page(object):
    def __init__(self, template_matcher: PageTemplateMatcher):
        self.matcher: PageTemplateMatcher = template_matcher

    def __getattr__(self, name):
        if name not in self.matcher.locators:
            raise AttributeError(f'No attribute "{name}" exists on object and no key of "{name}" exists in matchers locator dictionary.')
        if self.matcher.locators[name].element is None or not self.matcher.locators[name]:
            result = self.matcher.locators[name].find()
            if result is None:
                raise NoSuchElementException(f"{self.matcher.locators[name].name} unable to locate element by {self.matcher.locators[name].by}, with locator '{self.matcher.locators[name].locator}'")
        return self.matcher.locators[name].element

    @staticmethod
    def randomly_wait(low, high):
        sleep(random.randint(low, high))

    def locate_window(self, timeout=-1):
        """
        Locate the correct window by cycling through the window handles and
        checking running the `PageTemplateMatcher` to confirm the correct
        window handle is currently selected.

        Set `timeout` to something other than -1 if you don't want it
        to attempt to locate the window forever.

        :timeout:
        :return:
        """
        t1 = time()
        print(f'Trying to locate window that matches {self.__class__.__name__}')
        while True:
            for wh in self.matcher.driver.window_handles:
                self.matcher.driver.switch_to.window(wh)
                if self.matches(debug=True):
                    print(f'Found window for {self.__class__.__name__}')
                    return
                if -1 < timeout < time() - t1:
                    raise Exception(f'Cannot located window handle matching {self.__class__.__name__} in {timeout} seconds.')

    def matches(self, debug=False, timeout=.01):
        """
        Use this `Page`'s `PageTemplateMatcher` to check that the current web
        page matches the `PageTemplateMatcher`.

        :param debug:
        :return:
        """
        return self.matcher.matches(debug=debug, timeout=timeout)

    def locator(self, locator_name: str):
        """
        Get the `Locator` instance using the `Locator`'s lookup name.

        :param locator_name:
        :return:
        """
        return self.matcher.locators[locator_name]

    def wait_for_match(self, poll_frequency=.1, timeout=-1):
        print(f'Waiting for page to match {self.__class__.__name__}')
        t1 = time()
        while not self.matches(timeout=0):
            sleep(poll_frequency)
            if -1 < timeout < time() - t1:
                raise TimeoutException(f'No match for {self.__class__.__name__} found in {timeout} seconds.')
        print(f'Page matches {self.__class__.__name__}!')
        return self

    def wait_for_no_match(self, poll_frequency=.1, timeout=-1):
        print(f'Waiting for page to no longer match {self.__class__.__name__}')
        t1 = time()
        while self.matches(timeout=0):
            sleep(poll_frequency)
            if -1 < timeout < time() - t1:
                raise TimeoutException(f"Page continued to match {self.__class__.__name__} for {timeout} seconds.")
        print(f'Page no longer matches {self.__class__.__name__}.')
        return self

    def wait_until_ready(self, timeout=60, poll_frequency=.5):
        """
        Wait until the document readyState == complete

        :param timeout:
        :param poll_frequency:
        :return:
        """
        print('Waiting until DOM is ready.')
        sleep(1)
        WebDriverWait(self.matcher.driver, timeout, poll_frequency).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        print('DOM ready.')

    def wait_for(self, element: Locator, expected_condition, timeout=5, poll_frequency=.1):
        """
        Wait for an element to match an expected condition.

        :param element:
        :param expected_condition:
        :param timeout:
        :param poll_frequency:
        :return:
        """
        print(f'Waiting for "{element.name}" to be found by "{element.by}": "{element.locator}", to meet {expected_condition}')
        WebDriverWait(self.matcher.driver, timeout if timeout else 0.1, poll_frequency).until(
            expected_condition((element.by, element.locator))
        )

