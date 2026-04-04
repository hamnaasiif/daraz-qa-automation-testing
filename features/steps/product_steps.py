"""
Step definitions for product features
"""
from behave import when, then
from pages.search_page import SearchPage
from pages.product_page import ProductPage

@when('I click on the first product')
def step_click_first_product(context):
    """Click on first product in search results"""
    search_page = SearchPage(context.page)
    search_page.click_first_product()
    
    context.page.wait_for_timeout(2000)
    
    pages = context.page.context.pages
    if len(pages) > 1:
        context.product_page_obj = pages[-1]
    else:
        context.product_page_obj = context.page

@then('I should see product details page')
def step_verify_product_page(context):
    """Verify product page loaded"""
    product_page = ProductPage(context.product_page_obj)
    assert product_page.is_loaded(), "Product page did not load!"

@then('product name should be displayed')
def step_verify_product_name(context):
    """Verify product name exists"""
    product_page = ProductPage(context.product_page_obj)
    name = product_page.get_product_name()
    assert len(name) > 0, "Product name not found!"
    print(f"Product: {name[:50]}...")

@then('product price should be displayed')
def step_verify_product_price(context):
    """Verify product price exists"""
    product_page = ProductPage(context.product_page_obj)
    price = product_page.get_product_price()
    assert len(price) > 0, "Product price not found!"
    print(f"Price: {price}")

@then('I take a screenshot of the product')
def step_screenshot_product(context):
    """Take screenshot of product page"""
    product_page = ProductPage(context.product_page_obj)
    product_page.take_screenshot("product_page")