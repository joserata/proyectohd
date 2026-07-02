import os
import unittest

from playwright.sync_api import sync_playwright


class LoginSmokeTest(unittest.TestCase):
    base_url = os.getenv('PLAYWRIGHT_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
    developer_user = os.getenv('PLAYWRIGHT_DEV_USER', '')
    developer_password = os.getenv('PLAYWRIGHT_DEV_PASSWORD', '')
    tester_user = os.getenv('PLAYWRIGHT_TEST_USER', '')
    tester_password = os.getenv('PLAYWRIGHT_TEST_PASSWORD', '')

    def _login(self, page, username, password, profile):
        page.goto(f'{self.base_url}/login/', wait_until='domcontentloaded')
        page.get_by_label('Usuario').fill(username)
        page.get_by_label('Contraseña').fill(password)
        page.get_by_label('Perfil').select_option(label=profile)
        page.get_by_role('button', name='Entrar').click()
        page.wait_for_load_state('networkidle')

    def test_developer_profile_login(self):
        if not self.developer_user or not self.developer_password:
            self.skipTest('Faltan PLAYWRIGHT_DEV_USER o PLAYWRIGHT_DEV_PASSWORD')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1440, 'height': 1200})
            try:
                self._login(page, self.developer_user, self.developer_password, 'Desarrollo')
                self.assertIn('/dashboard', page.url)
            finally:
                browser.close()

    def test_tester_profile_login(self):
        if not self.tester_user or not self.tester_password:
            self.skipTest('Faltan PLAYWRIGHT_TEST_USER o PLAYWRIGHT_TEST_PASSWORD')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1440, 'height': 1200})
            try:
                self._login(page, self.tester_user, self.tester_password, 'Tester')
                self.assertIn('/pruebastest/', page.url)
            finally:
                browser.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
