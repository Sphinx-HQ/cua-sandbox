from playwright.sync_api import Browser, Page
from .base_playwright import BasePlaywrightComputer
from utils import get_auth_data
import config


class LocalPlaywrightComputer(BasePlaywrightComputer):
    """Launches a local Chromium instance using Playwright."""

    def __init__(self, headless: bool = False):
        super().__init__()

        self.headless = headless

        auth_data = get_auth_data(config.BITWARDEN_CLIENT_ID, config.BITWARDEN_CLIENT_SECRET, config.BITWARDEN_MASTER_PASSWORD)
        self.hubspot_email = auth_data["username"]
        self.hubspot_password = auth_data["password"]
        self.totp_code = auth_data["totp_code"]

    def _login_to_hubspot(self, page: Page) -> Page:
        """Handle HubSpot login process and return the logged-in page."""
        if not self.hubspot_email or not self.hubspot_password:
            raise ValueError("HubSpot credentials are required")

        # Fill in email and continue
        page.fill('input[type="email"]', self.hubspot_email)
        page.click('button[type="submit"]')

        # Click on "sign in with password" button first
        page.click('text="Or sign in with your HubSpot password instead"')

        # Wait for and fill in password
        page.wait_for_selector('input[type="password"]')
        page.fill('input[type="password"]', self.hubspot_password)
        page.click('button[type="submit"]')

        # Click on secondary verification method
        page.click('text="Use your secondary verification method"')

        # Handle TOTP 2FA
        page.wait_for_selector('input[type="text"]')  # Wait for TOTP input field
        page.fill('input[type="text"]', self.totp_code)
        page.click('button[type="submit"]')

        # Check for and click "Remember me" if it appears
        try:
            remember_button = page.wait_for_selector('button:has-text("Remember me")', timeout=5000)
            if remember_button:
                remember_button.click()
        except:
            pass

        # Wait for the dashboard to load and return the page
        page.wait_for_url("**/home/**", timeout=30000)
        return page

    def _get_browser_and_page(self) -> tuple[Browser, Page]:
        width, height = self.dimensions
        launch_args = [f"--window-size={width},{height}", "--disable-extensions", "--disable-file-system"]
        browser = self._playwright.chromium.launch(
            chromium_sandbox=True,
            headless=self.headless,
            args=launch_args,
            env={}
        )
        page = browser.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.goto("https://app.hubspot.com/login")

        # Login and get the logged-in page
        page = self._login_to_hubspot(page)

        return browser, page
