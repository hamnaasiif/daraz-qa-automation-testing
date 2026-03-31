"""
Base Page - Common methods for all pages
Provides reusable page object methods with Allure reporting
"""
from playwright.sync_api import Page
import os
import time
from datetime import datetime
from allure import step

class BasePage:
    """Base page class with common web operations and Allure integration"""
    
    def __init__(self, page: Page):
        """Initialize BasePage with a Playwright page instance
        
        Args:
            page: Playwright Page object for browser interaction
        """
        self.page = page
    
    @step("Navigate to {url}")
    def go_to(self, url: str, retries: int = 3) -> None:
        """Navigate to specified URL with retry logic.

        Uses 'domcontentloaded' instead of the default 'load' event so that
        navigation is considered complete as soon as the DOM is ready — well
        before heavy third-party scripts (ads, trackers) finish loading.
        Retries up to *retries* times with increasing timeouts before failing.

        Args:
            url: The complete URL to navigate to
            retries: Number of attempts before raising (default 3)

        Raises:
            TimeoutError: If all retry attempts are exhausted
        """
        print(f"Going to: {url}")
        timeouts = [60000, 90000, 120000]  # ms per attempt
        last_error = None
        for attempt in range(retries):
            try:
                self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=timeouts[min(attempt, len(timeouts) - 1)],
                )
                return  # success
            except Exception as e:
                last_error = e
                print(f"Navigation attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    wait_sec = 3 * (attempt + 1)
                    print(f"Retrying in {wait_sec}s…")
                    time.sleep(wait_sec)
        raise last_error
    
    @step("Click on element: {selector}")
    def click(self, selector: str) -> None:
        """Click on element matching the selector
        
        Playwright auto-waits for element to be visible and actionable
        before clicking. No manual wait needed.
        
        Args:
            selector: CSS selector or Playwright locator string
            
        Raises:
            TimeoutError: If element not found within timeout
        """
        print(f"Clicking: {selector}")
        self.page.click(selector)
    
    @step("Type '{text}' in {selector}")
    def type_text(self, selector: str, text: str) -> None:
        """Type text into an input field
        
        Playwright auto-waits for element to be ready before typing.
        Automatically clears existing text before typing.
        
        Args:
            selector: CSS selector or Playwright locator string
            text: Text to type into the field
            
        Raises:
            TimeoutError: If element not found or not interactive
        """
        print(f"Typing: {text}")
        self.page.fill(selector, text)
    
    @step("Get text from {selector}")
    def get_text(self, selector: str) -> str:
        """Get inner text from element
        
        Playwright auto-waits for element to be visible before extracting text.
        Uses inner_text() which returns visible text.
        
        Args:
            selector: CSS selector or Playwright locator string
            
        Returns:
            str: The inner text content of the element
            
        Raises:
            TimeoutError: If element not found within timeout
        """
        text = self.page.locator(selector).inner_text()
        print(f"Got text: {text}")
        return text
    
    @step("Check if element is visible: {selector}")
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible on the page
        
        Uses Playwright's built-in visibility checking.
        No manual waits - Playwright handles auto-wait.
        
        Args:
            selector: CSS selector or Playwright locator string
            
        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            return self.page.locator(selector).is_visible()
        except Exception as e:
            print(f"Element not visible: {selector}")
            return False
    
    @step("Take screenshot: {name}")
    def take_screenshot(self, name: str) -> str:
        """Take screenshot of current page and save to file
        
        Creates screenshots directory if it doesn't exist.
        Adds timestamp to filename for uniqueness.
        
        Args:
            name: Base name for the screenshot file (timestamp added automatically)
            
        Returns:
            str: Full path to the saved screenshot file
        """
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{name}_{timestamp}.png"
        self.page.screenshot(path=path)
        print(f"Screenshot: {path}")
        return path
    
    @step("Press key: {key}")
    def press_key(self, key: str) -> None:
        """Press a keyboard key
        
        Allows interacting with keyboard (Enter, Escape, etc.)
        
        Args:
            key: Key name (e.g., 'Enter', 'Escape', 'ArrowDown')
        """
        self.page.keyboard.press(key)
    
    @step("Get page title")
    def get_title(self) -> str:
        """Get the title of the current page
        
        Returns:
            str: The page title from <title> tag
        """
        return self.page.title()
    
    @step("Get current URL")
    def get_url(self) -> str:
        """Get the current page URL
        
        Returns:
            str: The complete URL of current page
        """
        return self.page.url