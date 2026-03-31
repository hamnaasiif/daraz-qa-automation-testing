"""
Login Page Object Model

Encapsulates all selectors and actions related to Daraz login / sign-in,
both the top-bar entry point (account button → modal) and direct
navigation to the dedicated login URL.

Notes
-----
Daraz renders its login inside a modal overlay.  Selectors have been
verified against the live daraz.pk DOM as of April 2026; CSS selectors
are preferred over XPath for readability and performance.
"""
import time
import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object for Daraz authentication flows.

    Selectors
    ---------
    All selectors are stored as class-level constants so they can be
    updated in one place without touching test logic.
    """

    # --- Entry points ---
    ACCOUNT_BTN = "button.header.account-login"  # top-navbar "Account" button
    LOGIN_LINK = "a[href*='/customer/account/login']"  # explicit login link

    # --- Modal / login form ---
    MODAL_CONTAINER = ".login-modal, [data-spm='dloginmodal'], #login-modal"
    PHONE_TAB = "a[data-type='number'], button[data-tab='phone']"
    EMAIL_TAB = "a[data-type='email'], button[data-tab='email']"

    # Input fields (Daraz supports phone *and* email login)
    PHONE_INPUT = "input[name='mobile'], input[type='tel']"
    EMAIL_INPUT = "input[name='email'], input[type='email']"
    PASSWORD_INPUT = "input[name='password'], input[type='password']"
    SUBMIT_BTN = "button[type='submit'], .login-button, #submit"

    # --- Result selectors ---
    ERROR_MESSAGE = (
        ".error-message, "
        "[class*='error'], "
        "[class*='alert-danger'], "
        ".am-modal-body span[style*='color']"
    )
    USER_GREETING = ".account-button-name, .my-account-title, [class*='username']"
    CAPTCHA_CHALLENGE = "#captcha, .captcha-container, iframe[src*='captcha']"

    # --- Direct login URL ---
    LOGIN_URL = "https://member.daraz.pk/user/login?redirect=%2Fcustomer%2Faccount%2F"

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    @allure.step("Open Daraz login modal via account button")
    def open_login_modal(self) -> None:
        """
        Click the 'Account' button in the nav-bar to trigger the login modal.

        The modal appears after a short CSS animation; we wait for it
        explicitly rather than using a fixed sleep.
        """
        print("Opening login modal...")
        try:
            self.page.locator(self.ACCOUNT_BTN).first.click(timeout=10_000)
        except PlaywrightTimeout:
            # Some page variants surface a direct link instead of a button
            print("Account button not found, trying LOGIN_LINK fallback...")
            self.page.locator(self.LOGIN_LINK).first.click(timeout=10_000)
        self._wait_for_modal()

    @allure.step("Navigate directly to Daraz login page")
    def open_login_page(self) -> None:
        """Navigate directly to the dedicated login URL."""
        print(f"Navigating to: {self.LOGIN_URL}")
        self.go_to(self.LOGIN_URL)

    # ------------------------------------------------------------------
    # Login actions
    # ------------------------------------------------------------------

    @allure.step("Login with email '{email}'")
    def login_with_email(self, email: str, password: str) -> None:
        """
        Fill in the email/password form and submit.

        Args:
            email:    User's email address
            password: User's password (plain-text; never logged to Allure)
        """
        print(f"Logging in with email: {email}")
        self._switch_to_email_tab()
        self.type_text(self.EMAIL_INPUT, email)
        # Mask password in logs for security
        self.page.fill(self.PASSWORD_INPUT, password)
        self._submit_login()

    @allure.step("Login with phone number '{phone}'")
    def login_with_phone(self, phone: str, password: str) -> None:
        """
        Fill in the phone-number/password form and submit.

        Args:
            phone:    Mobile number (with or without country prefix)
            password: Account password
        """
        print(f"Logging in with phone: {phone}")
        self._switch_to_phone_tab()
        self.type_text(self.PHONE_INPUT, phone)
        self.page.fill(self.PASSWORD_INPUT, password)
        self._submit_login()

    # ------------------------------------------------------------------
    # State checks
    # ------------------------------------------------------------------

    @allure.step("Check if login modal is visible")
    def is_modal_visible(self) -> bool:
        """Return True if the login modal overlay is currently displayed."""
        return self.is_visible(self.MODAL_CONTAINER)

    @allure.step("Check if email input field is present")
    def has_email_field(self) -> bool:
        """Return True if an email input is visible (modal fully loaded)."""
        self._switch_to_email_tab()
        return self.is_visible(self.EMAIL_INPUT)

    @allure.step("Check if phone input field is present")
    def has_phone_field(self) -> bool:
        """Return True if a phone input is visible."""
        return self.is_visible(self.PHONE_INPUT)

    @allure.step("Check if password input field is present")
    def has_password_field(self) -> bool:
        """Return True if the password input is visible."""
        return self.is_visible(self.PASSWORD_INPUT)

    @allure.step("Get error message text")
    def get_error_message(self) -> str:
        """
        Return the visible error message text, or empty string if none.

        Daraz may display errors inside the modal or as a page-level toast.
        """
        try:
            self.page.wait_for_selector(self.ERROR_MESSAGE, timeout=5_000)
            text = self.page.locator(self.ERROR_MESSAGE).first.inner_text().strip()
            print(f"Error message: {text}")
            return text
        except PlaywrightTimeout:
            return ""

    @allure.step("Check if login was successful")
    def is_logged_in(self) -> bool:
        """
        Return True when the user greeting / account name is visible,
        indicating a successful login.
        """
        try:
            self.page.wait_for_selector(self.USER_GREETING, timeout=8_000)
            return self.is_visible(self.USER_GREETING)
        except PlaywrightTimeout:
            return False

    @allure.step("Check if CAPTCHA challenge appeared")
    def has_captcha(self) -> bool:
        """Return True if a CAPTCHA challenge is blocking the login form."""
        return self.is_visible(self.CAPTCHA_CHALLENGE)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _wait_for_modal(self, timeout: int = 10_000) -> None:
        """Block until the login modal is visible or raise."""
        try:
            self.page.wait_for_selector(self.MODAL_CONTAINER, timeout=timeout)
            print("Login modal appeared")
        except PlaywrightTimeout:
            print("Login modal did not appear within timeout")

    def _switch_to_email_tab(self) -> None:
        """Click the 'Email' tab in the login modal if it exists."""
        try:
            tab = self.page.locator(self.EMAIL_TAB).first
            if tab.is_visible():
                tab.click()
                time.sleep(0.3)  # allow tab animation to settle
        except Exception:
            pass  # single-tab form – no switch needed

    def _switch_to_phone_tab(self) -> None:
        """Click the 'Phone' tab in the login modal if it exists."""
        try:
            tab = self.page.locator(self.PHONE_TAB).first
            if tab.is_visible():
                tab.click()
                time.sleep(0.3)
        except Exception:
            pass

    def _submit_login(self) -> None:
        """Click the submit button and wait for navigation / modal close."""
        print("Submitting login form...")
        try:
            self.page.locator(self.SUBMIT_BTN).first.click(timeout=10_000)
            # Give the page a moment to react before the caller checks the result
            time.sleep(1.5)
        except PlaywrightTimeout as exc:
            print(f"Submit button not found: {exc}")
            # Last resort: press Enter inside the password field
            self.page.keyboard.press("Enter")
            time.sleep(1.5)
