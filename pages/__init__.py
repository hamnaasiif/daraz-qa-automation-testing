"""
Pages package - Contains all page objects following the POM pattern.
"""
from pages.base_page import BasePage
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.product_page import ProductPage
from pages.login_page import LoginPage
from pages.cart_page import CartPage

__all__ = [
    'BasePage',
    'HomePage',
    'SearchPage',
    'ProductPage',
    'LoginPage',
    'CartPage',
]
