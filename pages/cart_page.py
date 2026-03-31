"""
Cart Page Object Model

Encapsulates all selectors and interactions related to the Daraz
shopping cart — viewing cart contents, modifying quantities, and
proceeding to checkout.

Design notes
------------
* Daraz renders the mini-cart as a sidebar overlay AND has a dedicated
  /cart/ page.  This POM handles both surfaces.
* All public methods are decorated with @allure.step for rich reporting.
* No fixed time.sleep() calls — Playwright's auto-wait is used throughout.
"""
import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from pages.base_page import BasePage


class CartPage(BasePage):
    """
    Page Object for Daraz shopping cart flows.

    Selectors
    ---------
    Constants below cover both the mini-cart sidebar and the full /cart/ page.
    """

    # --- Cart entry points (from any page) ---
    CART_ICON = ".nav-cart, [data-spm='cart'], a[href*='/cart/']"
    MINI_CART_DRAWER = ".mini-cart, .cart-sidebar, [class*='CartModal']"

    # --- Cart page (/cart/) ---
    CART_URL = "https://cart.daraz.pk/cart"
    CART_ITEMS_CONTAINER = ".cart-item-list, .cart-body, [class*='CartItem']"
    CART_ITEM = ".cart-item, [class*='cart-item'], .item-row"
    ITEM_NAME = ".item-name, .cart-name, [class*='itemTitle']"
    ITEM_PRICE = ".item-price, [class*='price'], .cart-price"
    ITEM_QTY_INPUT = "input[class*='quantity'], input[name='quantity'], .qty-input"
    QTY_INCREASE_BTN = "button[class*='increase'], .qty-plus, [data-action='increase']"
    QTY_DECREASE_BTN = "button[class*='decrease'], .qty-minus, [data-action='decrease']"
    REMOVE_BTN = "button[class*='remove'], .delete-btn, [data-action='delete']"

    # --- Pricing summary ---
    SUBTOTAL = ".subtotal-price, .order-total, [class*='SubTotal']"
    CHECKOUT_BTN = "button[class*='checkout'], a[class*='checkout'], .checkout-btn"

    # --- Empty cart state ---
    EMPTY_CART_MSG = ".empty-cart, [class*='EmptyCart'], .cart-empty-text"

    # --- Add-to-cart (product page) ---
    ADD_TO_CART_BTN = (
        "button[data-spm='addtocart'], "
        "button[class*='add-to-cart'], "
        ".btn-add-to-cart, "
        "#add-to-cart-btn"
    )
    BUY_NOW_BTN = "button[data-spm='buynow'], .btn-buynow, #buy-now-btn"

    # --- Login prompt (for guest users) ---
    LOGIN_PROMPT = ".login-modal, [class*='LoginModal'], .account-login"

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    @allure.step("Open shopping cart page")
    def open_cart(self) -> None:
        """Navigate directly to the Daraz cart page."""
        print(f"Navigating to cart: {self.CART_URL}")
        self.go_to(self.CART_URL)

    @allure.step("Open mini-cart sidebar via cart icon")
    def open_mini_cart(self) -> None:
        """Click the cart icon in the nav-bar to open the mini-cart sidebar."""
        print("Clicking cart icon...")
        try:
            self.page.locator(self.CART_ICON).first.click(timeout=8_000)
            self.page.wait_for_selector(self.MINI_CART_DRAWER, timeout=5_000)
            print("Mini-cart opened")
        except PlaywrightTimeout:
            print("Mini-cart did not open within timeout")

    # ------------------------------------------------------------------
    # Add-to-cart actions (used from ProductPage context)
    # ------------------------------------------------------------------

    @allure.step("Click 'Add to Cart' button")
    def click_add_to_cart(self) -> None:
        """
        Click the primary Add-to-Cart button on a product detail page.

        Raises:
            PlaywrightTimeout: If no matching button found within timeout
        """
        print("Clicking Add to Cart...")
        self.page.locator(self.ADD_TO_CART_BTN).first.click(timeout=10_000)

    @allure.step("Click 'Buy Now' button")
    def click_buy_now(self) -> None:
        """Click the Buy Now button to go straight to checkout."""
        print("Clicking Buy Now...")
        self.page.locator(self.BUY_NOW_BTN).first.click(timeout=10_000)

    # ------------------------------------------------------------------
    # Cart content inspection
    # ------------------------------------------------------------------

    @allure.step("Check if cart has items")
    def has_items(self) -> bool:
        """Return True if at least one item is visible in the cart."""
        try:
            self.page.wait_for_selector(self.CART_ITEM, timeout=5_000)
            count = self.page.locator(self.CART_ITEM).count()
            print(f"Cart item count: {count}")
            return count > 0
        except PlaywrightTimeout:
            return False

    @allure.step("Get cart item count")
    def get_item_count(self) -> int:
        """Return the number of distinct line items in the cart."""
        try:
            return self.page.locator(self.CART_ITEM).count()
        except Exception:
            return 0

    @allure.step("Get cart subtotal text")
    def get_subtotal(self) -> str:
        """
        Return the displayed subtotal string (e.g. 'Rs. 45,000').

        Returns:
            str: Subtotal text, or empty string if not found
        """
        try:
            self.page.wait_for_selector(self.SUBTOTAL, timeout=5_000)
            text = self.page.locator(self.SUBTOTAL).first.inner_text().strip()
            print(f"Subtotal: {text}")
            return text
        except PlaywrightTimeout:
            return ""

    @allure.step("Check if cart is empty")
    def is_empty(self) -> bool:
        """Return True when the empty-cart illustration / message is shown."""
        return self.is_visible(self.EMPTY_CART_MSG)

    @allure.step("Check if 'Add to Cart' button is visible")
    def has_add_to_cart_button(self) -> bool:
        """Return True if the Add-to-Cart CTA is visible on the current page."""
        return self.is_visible(self.ADD_TO_CART_BTN)

    @allure.step("Check if login prompt appeared after cart action")
    def has_login_prompt(self) -> bool:
        """
        Return True if Daraz redirected the guest user to a login screen
        after they attempted to add an item or proceed to checkout.
        """
        return self.is_visible(self.LOGIN_PROMPT)

    # ------------------------------------------------------------------
    # Cart modification
    # ------------------------------------------------------------------

    @allure.step("Increase quantity of first cart item")
    def increase_quantity(self) -> None:
        """Click the + (increase) button on the first cart line item."""
        try:
            self.page.locator(self.QTY_INCREASE_BTN).first.click(timeout=8_000)
            print("Quantity increased")
        except PlaywrightTimeout:
            print("Increase-quantity button not found")

    @allure.step("Decrease quantity of first cart item")
    def decrease_quantity(self) -> None:
        """Click the − (decrease) button on the first cart line item."""
        try:
            self.page.locator(self.QTY_DECREASE_BTN).first.click(timeout=8_000)
            print("Quantity decreased")
        except PlaywrightTimeout:
            print("Decrease-quantity button not found")

    @allure.step("Remove first cart item")
    def remove_first_item(self) -> None:
        """Click the remove/delete button on the first cart line item."""
        try:
            self.page.locator(self.REMOVE_BTN).first.click(timeout=8_000)
            print("Item removed from cart")
        except PlaywrightTimeout:
            print("Remove button not found")

    # ------------------------------------------------------------------
    # Checkout flow
    # ------------------------------------------------------------------

    @allure.step("Proceed to checkout")
    def proceed_to_checkout(self) -> None:
        """
        Click the Checkout button.

        Daraz requires login for checkout; if a login modal appears the
        caller should handle it via LoginPage.
        """
        print("Proceeding to checkout...")
        try:
            self.page.locator(self.CHECKOUT_BTN).first.click(timeout=10_000)
        except PlaywrightTimeout:
            print("Checkout button not found - may require login first")

    # ------------------------------------------------------------------
    # Product-availability helpers (used in Scenario Outlines)
    # ------------------------------------------------------------------

    @allure.step("Get product price from current product detail page")
    def get_product_price(self) -> str:
        """
        Return the price string shown on the current product detail page.

        Returns:
            str: Price text or empty string
        """
        price_selectors = [
            ".pdp-price, .origin-block-price",
            "[class*='pdp-price']",
            ".notranslate.pdp-price",
            "span[class*='price']",
        ]
        for sel in price_selectors:
            try:
                el = self.page.locator(sel).first
                if el.is_visible():
                    text = el.inner_text().strip()
                    print(f"Product price: {text}")
                    return text
            except Exception:
                continue
        print("Price not found")
        return ""

    @allure.step("Check product availability")
    def get_availability_status(self) -> str:
        """
        Return a normalised availability string: 'in-stock' or 'out-of-stock'.

        Daraz does not always show an explicit stock label; the presence of
        the Add-to-Cart button is used as a proxy for in-stock status.
        """
        in_stock_indicators = [
            "button[data-spm='addtocart']",
            "button[class*='add-to-cart']",
            ".btn-add-to-cart",
        ]
        out_of_stock_indicators = [
            ".sold-out, [class*='SoldOut']",
            ".out-of-stock",
            "button[disabled][class*='addtocart']",
        ]

        for sel in out_of_stock_indicators:
            if self.is_visible(sel):
                print("Product is OUT OF STOCK")
                return "out-of-stock"

        for sel in in_stock_indicators:
            if self.is_visible(sel):
                print("Product is IN STOCK")
                return "in-stock"

        # Could not determine – treat conservatively
        print("Stock status unknown - assuming in-stock")
        return "in-stock"
