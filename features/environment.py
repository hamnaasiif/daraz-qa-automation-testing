"""
Behave Environment - Hooks for setup/teardown
"""
from utils.browser_factory import BrowserFactory
from utils.config import Config

def before_all(context):
    """Run once before all tests"""
    print("\n" + "="*60)
    print("STARTING TEST SUITE")
    print("="*60)
    context.config_data = Config()

def before_scenario(context, scenario):
    """Run before each scenario"""
    print(f"Starting: {scenario.name}")
    
    try:
        # Start browser
        print(f"DEBUG: About to start browser with {Config.BROWSER}, headless={Config.HEADLESS}")
        context.page = BrowserFactory.start_browser(
            browser_type=Config.BROWSER,
            headless=Config.HEADLESS
        )
        print(f"DEBUG: Browser started, context.page = {context.page}")
    except Exception as e:
        print(f"ERROR in before_scenario: {e}")
        import traceback
        traceback.print_exc()
        raise

def after_scenario(context, scenario):
    """Run after each scenario"""
    
    # Take screenshot if failed
    if scenario.status == 'failed':
        print(f"Scenario FAILED: {scenario.name}")
        if hasattr(context, 'page'):
            from pages.base_page import BasePage
            base = BasePage(context.page)
            base.take_screenshot(f"FAILED_{scenario.name}")
    else:
        print(f"Scenario PASSED: {scenario.name}")
    
    # Close browser
    BrowserFactory.stop_browser()

def after_all(context):
    """Run once after all tests"""
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)