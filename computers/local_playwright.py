from playwright.sync_api import Browser, Page
from .base_playwright import BasePlaywrightComputer
import os

class LocalPlaywrightComputer(BasePlaywrightComputer):
    """Launches a local Chromium instance using Playwright."""

    def __init__(self, headless: bool = False):
        super().__init__()
        self.headless = headless
        self.hubspot_email = os.environ["HUBSPOT_EMAIL"]
        self.hubspot_password = os.environ["HUBSPOT_PASSWORD"]

    def _login_to_hubspot(self, page: Page) -> None:
        """Handle HubSpot login process."""
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

        # Wait for login to complete
        page.wait_for_url("**/home/**", timeout=30000)

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

        # Add login step
        self._login_to_hubspot(page)

        return browser, page
