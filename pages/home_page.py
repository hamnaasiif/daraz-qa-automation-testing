"""
Daraz Home Page
Implements page object methods for Daraz homepage interactions
"""
from pages.base_page import BasePage
from allure import step

class HomePage(BasePage):
    """Daraz homepage with search and navigation methods"""

    # Locators - multiple fallbacks for Daraz's dynamic class names
    SEARCH_BOX = 'input[type="search"]'
    SEARCH_BOX_ALT = '#q, [placeholder*="Search"], [name="q"]'
    SEARCH_BUTTON = 'button.search-box__button--1oH7'
    LOGO = 'img[alt="Daraz Logo"]'

    def __init__(self, page, url=None):
        """Initialize HomePage with optional custom URL

        Args:
            page: Playwright Page object
            url: Custom URL (default: https://www.daraz.pk)
        """
        super().__init__(page)
        self.url = url or "https://www.daraz.pk"

    @step("Open Daraz homepage")
    def open(self, max_attempts: int = 3) -> None:
        """Open Daraz homepage and wait until it is fully interactive.

        Sometimes Daraz returns a fast blank/redirect page whose
        domcontentloaded fires immediately but the search box is absent.
        This method retries the *entire* navigation up to max_attempts times
        if the search box is not found after landing.

        Args:
            max_attempts: Total navigation attempts before raising (default 3)
        """
        import time as _time

        print("Opening Daraz homepage...")

        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                # Navigate (domcontentloaded + internal retry handled by go_to)
                self.go_to(self.url)

                # Allow JS framework to hydrate; ignore if networkidle never fires
                try:
                    self.page.wait_for_load_state("networkidle", timeout=12000)
                except Exception:
                    print("networkidle timed out - continuing")

                # Wait for the search box to actually appear
                try:
                    self.page.wait_for_selector(self.SEARCH_BOX, timeout=20000)
                    print(f"Search box found on attempt {attempt}")
                    return  # success
                except Exception:
                    # DOM loaded but search box absent → Daraz served wrong page
                    current_url = self.page.url
                    print(
                        f"Search box not found after load "
                        f"(current url: {current_url}). "
                        f"Attempt {attempt}/{max_attempts}."
                    )
                    last_error = Exception(
                        f"Search box not visible after navigation to {current_url}"
                    )
            except Exception as e:
                last_error = e
                print(f"Navigation attempt {attempt}/{max_attempts} failed: {e}")

            if attempt < max_attempts:
                wait_sec = 5 * attempt
                print(f"Retrying in {wait_sec}s...")
                _time.sleep(wait_sec)

        raise last_error

    @step("Search for product: {product_name}")
    def search_product(self, product_name: str) -> None:
        """Search for a product on Daraz.

        Enters the search term and presses Enter, then waits for the catalog
        page navigation to complete (domcontentloaded) before returning.
        This prevents the next step from running while the page is still
        mid-navigation, which would cause element-not-found timeouts.

        Args:
            product_name: Name of the product to search for
        """
        print(f"Searching for: {product_name}")
        self.type_text(self.SEARCH_BOX, product_name)
        # Wait for the navigation triggered by Enter to complete
        with self.page.expect_navigation(
            wait_until="domcontentloaded", timeout=60000
        ):
            self.press_key('Enter')
        print(f"Catalog page loaded")

    @step("Check if homepage is loaded")
    def is_loaded(self) -> bool:
        """Check if homepage has loaded successfully

        Verifies that the search box is visible and accessible.
        By the time this is called, open() has already confirmed the
        search box is present, so this is a fast non-blocking check.

        Returns:
            bool: True if homepage is loaded, False otherwise
        """
        return self.is_visible(self.SEARCH_BOX)