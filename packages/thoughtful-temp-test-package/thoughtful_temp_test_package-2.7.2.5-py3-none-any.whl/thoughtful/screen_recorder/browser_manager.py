"""Classes for managing a browser via BrowserManager."""

import logging
from enum import Enum
from typing import Optional

from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import WebDriverException
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.errors import NoOpenBrowser

logger = logging.getLogger(__name__)


class BrowserManager:
    """A class for providing a common interface for the ScreenRecorder
    class to utilize when interacting with a browser
    """

    class BrowserManagerType(Enum):
        Selenium = "SELENIUM"

    def __init__(self, instance: SeleniumLibrary):
        """Initialize the ScreenRecorder.

        Args:
            instance (SeleniumLibrary): Instance that provides access to
            control the browser. Browser operations should be performable
            on this instance.

        Example:
            from RPA.Browser.Selenium import Selenium  # installed separately
            from thoughtful.screen_recorder import BrowserManager

            selenium_instance = Selenium()
            browser_manager = BrowserManager(instance=selenium_instance)
        """
        self._instance: SeleniumLibrary = instance

        if isinstance(self._instance, SeleniumLibrary):
            self._browser_manager_type = self.BrowserManagerType.Selenium
        else:
            raise ValueError("Invalid BrowserManager instance provided.")

    def get_connection_pool_size(self) -> Optional[int]:
        return self._instance.driver.command_executor._conn.connection_pool_kw.get(
            "maxsize"
        )

    def update_connection_pool_size(self, max_connections: int):
        self._instance.driver.command_executor._conn.connection_pool_kw[
            "maxsize"
        ] = max_connections
        logger.info("Clearing existing connection pool to apply new pool size.")
        self._instance.driver.command_executor._conn.clear()

    def is_browser_open(self) -> bool:
        """Check if the browser is open."""
        if self._browser_manager_type == self.BrowserManagerType.Selenium:
            try:
                # Call driver getter - it will throw an error if the driver
                # is not yet opened
                self._instance.driver
                return True
            except NoOpenBrowser:
                return False
            except InvalidSessionIdException:
                # The browser session is not currently active - this likely
                # means the session crashed or was deleted. We should
                # return `False` to indicate that the page is not in a
                # valid `loaded` state.
                return False
        else:
            raise ValueError("Invalid BrowserManager instance provided.")

    def has_page_loaded(self) -> bool:
        """Check if the browser window is loaded."""
        if self._browser_manager_type == self.BrowserManagerType.Selenium:
            try:
                return self._instance.driver.current_url != "data:,"
            except UnexpectedAlertPresentException:
                # Thrown when an unexpected alert has appeared.
                # Usually raised when an unexpected modal is blocking the
                # webdriver from executing commands.
                # We return True here because a model appearing would
                # indicate that content has loaded on the page.
                return True
            except InvalidSessionIdException:
                # The browser session is not currently active - this likely
                # means the session crashed or was deleted. We should
                # return `False` to indicate that the page is not in a
                # valid `loaded` state.
                return False
            except WebDriverException as e:
                # Catch-all WebDriver exception that we default to if specific
                # exceptions are not detected
                logger.warning(
                    f"An unexpected WebDriverException occurred "
                    f"and was handled: {e}."
                )
                return False

        else:
            raise ValueError("Invalid BrowserManager instance detected.")

    def get_base64_screenshot(self) -> str:
        """Take screenshot and output as base64 string."""
        if self._browser_manager_type == self.BrowserManagerType.Selenium:
            base64_screenshot = self._instance.driver.get_screenshot_as_base64()
        else:
            raise ValueError("Invalid BrowserManager instance provided.")
        return base64_screenshot
