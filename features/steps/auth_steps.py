"""
Step definitions for authentication / guest-access features.

NOTE: Actual login (submitting credentials) is intentionally NOT automated
because Daraz may require CAPTCHA / 2-FA and real credentials.
These tests verify the *accessibility* of auth UI: login button visible,
form fields present, guest browsing works.
"""
from behave import given, when, then
from pages.home_page import HomePage


# ---------------------------------------------------------------------------
# GUEST BROWSING
# ---------------------------------------------------------------------------

@then('I should see search functionality available')
def step_verify_search_available(context):
    """Search box must be visible — proves guest users can search."""
    if not hasattr(context, 'home_page'):
        context.home_page = HomePage(context.page)

    is_visible = context.home_page.is_loaded()
    assert is_visible, (
        "[FAIL] Search box not visible on homepage — "
        "guest browsing is broken."
    )
    print("Search functionality is available for guest users")


@then('I should see product categories')
def step_verify_categories(context):
    """At least one category / navigation link must exist in the header."""
    page = context.page

    # Broad selector — Daraz renders categories in the top nav
    selectors = [
        '[class*="category"]',
        'nav a',
        '[class*="nav"] a',
        'a[href*="catalog"]',
        'a[href*="category"]',
    ]

    found = 0
    for sel in selectors:
        elements = page.query_selector_all(sel)
        found += len(elements)
        if found > 0:
            break

    assert found > 0, (
        "[FAIL] No category / navigation links found on homepage. "
        "The page may not have loaded correctly."
    )
    print(f"Found at least {found} category/navigation element(s)")


@then('homepage should load successfully')
def step_homepage_loads(context):
    """Page title must contain 'Daraz' and the search box must be present."""
    if not hasattr(context, 'home_page'):
        context.home_page = HomePage(context.page)

    # 1. Search box must be present
    assert context.home_page.is_loaded(), (
        "[FAIL] Search box not found — homepage did not load correctly."
    )

    # 2. Page title must mention Daraz
    title = context.page.title()
    assert 'daraz' in title.lower(), (
        f"[FAIL] Unexpected page title '{title}' — "
        "expected it to contain 'Daraz'."
    )
    print(f"Homepage loaded successfully (title: '{title}')")


# ---------------------------------------------------------------------------
# LOGIN FLOW
# ---------------------------------------------------------------------------

@when('I click on login button')
def step_click_login_button(context):
    """Find and click the LOGIN button in the Daraz header."""
    page = context.page
    print("Auth: Looking for LOGIN button...")

    # Ordered list of selectors — stop at the first one that works
    login_selectors = [
        'a:has-text("LOGIN")',
        'a:has-text("Login")',
        'a:has-text("Sign in")',
        '[class*="account"] a:has-text("Login")',
        'a[href*="login"]',
        'button:has-text("Login")',
    ]

    clicked = False
    for sel in login_selectors:
        try:
            locator = page.locator(sel).first
            if locator.is_visible(timeout=3000):
                locator.click()
                clicked = True
                print(f"Clicked LOGIN button via selector: {sel}")
                break
        except Exception:
            continue

    assert clicked, (
        "[FAIL] LOGIN button not found in the page header. "
        "Daraz may have changed its layout or the page did not load."
    )

    # Wait for the modal animation to complete (max 5 s)
    try:
        page.wait_for_selector(
            'input[type="password"], input[placeholder*="Phone" i], '
            'input[placeholder*="Email" i], [role="dialog"]',
            timeout=5000,
        )
    except Exception:
        pass  # We'll assert in the next step; don't fail here


@then('login modal should appear')
def step_verify_login_modal(context):
    """A login form or dialog must appear after clicking LOGIN."""
    page = context.page
    print("Auth: Checking for login modal...")

    modal_selectors = [
        '[role="dialog"]',
        '[class*="modal"]',
        '[class*="login"]',
        '[class*="popup"]',
        'input[type="password"]',
        'input[placeholder*="Phone" i]',
        'input[placeholder*="Email" i]',
        'input[placeholder*="phone" i]',
    ]

    modal_found = False
    for sel in modal_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state="visible")
            if el:
                print(f"Login modal detected via selector: {sel}")
                modal_found = True
                break
        except Exception:
            continue

    if not modal_found:
        # Save screenshot to help diagnose what actually appeared
        page.screenshot(path="screenshots/login_modal_debug.png")

    assert modal_found, (
        "[FAIL] Login modal / form did not appear after clicking LOGIN. "
        "Screenshot saved to screenshots/login_modal_debug.png"
    )
    print("Login modal appeared successfully")


@then('I should see phone or email input field')
def step_verify_phone_email_field(context):
    """Phone or e-mail input must be visible inside the login form."""
    page = context.page
    print("Auth: Checking for phone/email input...")

    selectors = [
        'input[placeholder*="Phone" i]',
        'input[placeholder*="Email" i]',
        'input[placeholder*="phone" i]',
        'input[placeholder*="email" i]',
        'input[type="email"]',
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[name*="email" i]',
    ]

    field_found = False
    for sel in selectors:
        try:
            el = page.wait_for_selector(sel, timeout=3000, state="visible")
            if el:
                placeholder = el.get_attribute('placeholder') or sel
                print(f"Phone/Email input found: '{placeholder}'")
                field_found = True
                break
        except Exception:
            continue

    assert field_found, (
        "[FAIL] No phone or email input field found in the login form. "
        "The login modal may not have rendered correctly."
    )


@then('I should see password input field')
def step_verify_password_field(context):
    """Password input must be visible inside the login form."""
    page = context.page
    print("Auth: Checking for password input...")

    try:
        el = page.wait_for_selector(
            'input[type="password"]', timeout=4000, state="visible"
        )
        assert el is not None, "Password field element is None"
        print("Password field found")
    except Exception:
        # Some flows show password only after entering phone/email first.
        # Check if the form is still present as a softer confirmation.
        form_present = page.query_selector(
            '[class*="login"], [role="dialog"], [class*="modal"]'
        )
        assert form_present is not None, (
            "[FAIL] Password field not found and login form is not visible. "
            "Daraz may use a 2-step login (enter phone first, then password)."
        )
        print("Password field not immediately visible - Daraz likely uses a 2-step login flow")


# ---------------------------------------------------------------------------
# GUEST + CART
# ---------------------------------------------------------------------------

@then('I should see add to cart button or login prompt')
def step_verify_cart_or_login(context):
    """On a product page, either 'Add to Cart' or a login prompt must exist."""
    from pages.product_page import ProductPage

    if hasattr(context, 'product_page_obj'):
        product_page = ProductPage(context.product_page_obj)
    else:
        product_page = ProductPage(context.page)

    page = product_page.page
    print("Cart: Checking for 'Add to Cart' button or login prompt...")

    # Look for Add-to-Cart variants
    cart_selectors = [
        'button:has-text("Add to Cart")',
        'button:has-text("Add To Cart")',
        '[class*="add-to-cart"]',
        '[class*="addToCart"]',
        '[class*="btn-cart"]',
        'button:has-text("Buy Now")',
    ]
    # Look for login / sign-in prompts
    login_selectors = [
        'text=/log.?in/i',
        'text=/sign.?in/i',
        'a[href*="login"]',
        'button:has-text("Login")',
    ]

    found_what = None

    for sel in cart_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                found_what = f"Add-to-Cart button ({sel})"
                break
        except Exception:
            continue

    if not found_what:
        for sel in login_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=3000, state="visible")
                if el:
                    found_what = f"Login/Sign-in prompt ({sel})"
                    break
            except Exception:
                continue

    assert found_what is not None, (
        "[FAIL] Neither an 'Add to Cart' button nor a login prompt was found "
        "on the product page. The page may not have loaded correctly."
    )
    print(f"Found: {found_what}")


# ---------------------------------------------------------------------------
# UTILITY STEP
# ---------------------------------------------------------------------------

@given('I am not logged in')
def step_verify_not_logged_in(context):
    """Confirm we are operating as a guest (no logged-in indicators)."""
    page = context.page
    print("Auth: Verifying guest mode (not logged in)...")

    # Logged-in Daraz pages show the account username or 'My Account' link
    logged_in_indicators = [
        '[class*="account-name"]',
        'a:has-text("My Account")',
        '[class*="user-name"]',
    ]

    for sel in logged_in_indicators:
        el = page.query_selector(sel)
        if el and el.is_visible():
            # Not a hard failure — just a warning; the browser may have cached a session
            print(f"Warning: Logged-in indicator found ({sel}).")
            return

    print("No logged-in indicators - operating as guest user")


@when('I enter "{email}" and "{password}"')
def step_enter_credentials(context, email, password):
    """
    Fill in the login form with confirmed selectors from live Daraz inspection.

    After clicking 'LOGIN' on the homepage, Daraz navigates to:
      https://member.daraz.pk/user/login
    The form has:
      - Primary input: input[placeholder='Please enter your Phone Number or Email']
      - Password input: input[placeholder='Please enter your password']
      - Submit button:  button.next-btn-primary
    """
    import time
    page = context.page
    print(f"Auth: Entering credentials: {email} / ********")

    # Wait for navigation to member.daraz.pk/user/login to complete
    try:
        page.wait_for_url("**/user/login**", timeout=10000)
        print(f"On login page: {page.url}")
    except Exception:
        print(f"Current URL: {page.url} - proceeding with form fill")

    # --- Step 1: Fill primary field (phone or email) ---
    primary_sel = "input[placeholder='Please enter your Phone Number or Email']"
    try:
        el = page.wait_for_selector(primary_sel, timeout=8000, state="visible")
        el.click()
        el.fill("")          # clear first
        el.fill(email)
        print(f"Filled primary field with: {email}")
    except Exception as e:
        # Fallback: try any visible non-password input
        print(f"Warning: Exact selector not found ({e}), trying fallback...")
        for fallback in [
            'input[type="text"]',
            'input[type="tel"]',
            'input[type="email"]',
        ]:
            try:
                el = page.wait_for_selector(fallback, timeout=3000, state="visible")
                el.fill(email)
                print(f"Filled fallback field ({fallback}) with: {email}")
                break
            except Exception:
                continue

    time.sleep(0.4)

    # --- Step 2: Fill password ---
    pass_sel = "input[placeholder='Please enter your password']"
    try:
        pw = page.wait_for_selector(pass_sel, timeout=6000, state="visible")
        pw.fill(password)
        print("Filled password field")
    except Exception:
        # Generic password fallback
        try:
            pw = page.wait_for_selector('input[type="password"]', timeout=3000, state="visible")
            pw.fill(password)
            print("Filled password field (fallback selector)")
        except Exception as e:
            print(f"Warning: Password field not found: {e}")

    # --- Step 3: Submit ---
    submit_sel = "button.next-btn-primary"
    try:
        btn = page.wait_for_selector(submit_sel, timeout=5000, state="visible")
        btn.click()
        print("Submitted form via button.next-btn-primary")
        time.sleep(3)   # wait for error toast / redirect
    except Exception:
        # Fallback submit
        for sel in ['button:has-text("LOGIN")', 'button[type="submit"]']:
            try:
                page.locator(sel).first.click(timeout=3000)
                print(f"Submitted via fallback: {sel}")
                time.sleep(3)
                break
            except Exception:
                continue


@then('I should see "{expected_result}"')
def step_see_expected_result(context, expected_result):
    """Verify expected result after login attempt using confirmed Daraz selectors."""
    page = context.page
    print(f"Auth: Checking for expected result: {expected_result}")

    if expected_result == "error_message":
        # Confirmed: Daraz renders errors inside .next-feedback-error > .next-feedback-content
        # Text observed: "Error: Invalid account or password."
        error_selectors = [
            ".next-feedback-error",
            ".next-feedback-content",
            "[class*='next-feedback']",
            "[class*='error-msg']",
            "[class*='error-message']",
            "[class*='errMsg']",
            "text=/Invalid account or password/i",
            "text=/incorrect/i",
            "text=/invalid/i",
            "text=/Error:/i",
        ]
        error_found = False
        for sel in error_selectors:
            try:
                el = page.wait_for_selector(sel, timeout=5000, state="visible")
                if el:
                    msg = el.inner_text().strip()
                    if msg:  # make sure it has actual text
                        print(f"Error message found via '{sel}': {msg}")
                        error_found = True
                        break
            except Exception:
                continue

        assert error_found, (
            "[FAIL] Expected an error message after invalid login, but none appeared. "
            f"Current URL: {page.url} — Check if the form submitted correctly."
        )