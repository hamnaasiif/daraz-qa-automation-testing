"""
Browser Factory - Manages Playwright browser instances
"""
from playwright.sync_api import sync_playwright
import time

class BrowserFactory:
    """Factory to create and manage browser instances"""
    
    _playwright = None
    _browser = None
    _page = None
    _playwright_context = None
    
    @classmethod
    def start_browser(cls, browser_type="chromium", headless=False):
        """
        Start browser and return page - creates fresh Playwright instance for each browser
        
        Args:
            browser_type: chromium, firefox, or webkit
            headless: True for headless, False to see browser
        """
        print(f"[START] Starting {browser_type} browser...")
        
        # Close any previous browser
        try:
            cls.stop_browser()
        except:
            pass
        
        # Add small delay before starting new browser to allow cleanup
        time.sleep(0.5)
        
        # Create fresh Playwright context
        print("[DEBUG] Creating new Playwright instance...")
        cls._playwright_context = sync_playwright()
        cls._playwright = cls._playwright_context.start()
        
        # Browser launch args to improve connectivity
        launch_args = {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        }
        
        try:
            if browser_type == "chromium":
                cls._browser = cls._playwright.chromium.launch(**launch_args)
            elif browser_type == "firefox":
                cls._browser = cls._playwright.firefox.launch(
                    headless=headless,
                    args=['--no-sandbox'],
                )
            elif browser_type == "webkit":
                cls._browser = cls._playwright.webkit.launch(headless=headless)

            # Create browser context with realistic headers to reduce bot-detection
            context = cls._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1366, "height": 768},
                locale="en-PK",
                timezone_id="Asia/Karachi",
            )

            # Create new page from context
            cls._page = context.new_page()
            cls._page.set_default_timeout(30000)           # 30s for element waits
            cls._page.set_default_navigation_timeout(120000)  # 120s for navigation

            print("Browser started!")
            return cls._page
        except Exception as e:
            print(f"Failed to start browser: {e}")
            # Try to cleanup
            try:
                if cls._browser:
                    cls._browser.close()
                if cls._playwright:
                    cls._playwright.stop()
            except:
                pass
            raise
    
    @classmethod
    def stop_browser(cls):
        """Close current browser and Playwright instance"""
        print("Closing browser...")
        
        try:
            if cls._page:
                try:
                    cls._page.close()
                except Exception as e:
                    print(f"[WARN] Error closing page: {e}")
                cls._page = None
        except:
            pass
        
        try:
            if cls._browser:
                try:
                    cls._browser.close()
                except Exception as e:
                    print(f"[WARN] Error closing browser: {e}")
                cls._browser = None
        except:
            pass
        
        try:
            if cls._playwright_context:
                try:
                    cls._playwright.stop()
                except Exception as e:
                    print(f"[WARN] Error stopping playwright: {e}")
                cls._playwright = None
                cls._playwright_context = None
        except:
            pass
        
        print("Browser closed!")
    
    @classmethod
    def get_page(cls):
        """Get current page"""
        return cls._page