"""
Indeed Job Application Automation using Playwright
"""
from playwright.sync_api import sync_playwright, Page, TimeoutError
from typing import Dict, Optional
import time
import random

class IndeedApplicator:
    """Automate job applications on Indeed"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def apply_to_job(
        self,
        job_url: str,
        user_data: Dict,
        resume_path: str
    ) -> Dict:
        """
        Apply to a job on Indeed

        Args:
            job_url: Indeed job URL
            user_data: Dict with name, email, phone, etc.
            resume_path: Path to resume file

        Returns:
            Dict with success status and details
        """
        page = self.context.new_page()

        try:
            print(f"Navigating to: {job_url}")
            page.goto(job_url, wait_until='networkidle', timeout=30000)

            # Wait for page to load
            time.sleep(2)

            # Check if "Easy Apply" button exists
            easy_apply_button = self._find_apply_button(page)

            if not easy_apply_button:
                return {
                    'success': False,
                    'error': 'No apply button found - may require external application'
                }

            # Click apply button
            print("Clicking apply button...")
            easy_apply_button.click()
            time.sleep(2)

            # Check if login is required
            if self._is_login_page(page):
                return {
                    'success': False,
                    'error': 'Login required - Indeed account needed for auto-apply'
                }

            # Fill application form
            success = self._fill_application_form(page, user_data, resume_path)

            if success:
                return {
                    'success': True,
                    'message': 'Application submitted successfully',
                    'url': job_url
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to complete application form'
                }

        except TimeoutError:
            return {
                'success': False,
                'error': 'Page load timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            page.close()

    def _find_apply_button(self, page: Page) -> Optional[any]:
        """Find and return the apply button"""
        selectors = [
            'button[id*="apply"]',
            'button[id*="indeedApplyButton"]',
            'button:has-text("Apply now")',
            'a:has-text("Apply now")',
            '.jobsearch-IndeedApplyButton-newDesign'
        ]

        for selector in selectors:
            try:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    return button
            except:
                continue

        return None

    def _is_login_page(self, page: Page) -> bool:
        """Check if we're on a login page"""
        login_indicators = [
            'input[type="email"]',
            'input[name="email"]',
            '#login-email-input',
            'text=Sign in'
        ]

        for indicator in login_indicators:
            try:
                if page.query_selector(indicator):
                    return True
            except:
                continue

        return False

    def _fill_application_form(
        self,
        page: Page,
        user_data: Dict,
        resume_path: str
    ) -> bool:
        """Fill out the application form"""
        try:
            # Wait for form to appear
            time.sleep(2)

            # Fill name
            name_field = self._find_field(page, ['name', 'fullName', 'full-name'])
            if name_field:
                self._fill_field(name_field, user_data.get('name', ''))

            # Fill email
            email_field = self._find_field(page, ['email', 'emailAddress'])
            if email_field:
                self._fill_field(email_field, user_data.get('email', ''))

            # Fill phone
            phone_field = self._find_field(page, ['phone', 'phoneNumber', 'mobile'])
            if phone_field:
                self._fill_field(phone_field, user_data.get('phone', ''))

            # Upload resume
            resume_upload = page.query_selector('input[type="file"]')
            if resume_upload and resume_path:
                print("Uploading resume...")
                resume_upload.set_input_files(resume_path)
                time.sleep(2)

            # Look for additional questions and try to answer
            self._answer_screening_questions(page, user_data)

            # Submit application
            submit_button = self._find_submit_button(page)
            if submit_button:
                print("Submitting application...")
                submit_button.click()
                time.sleep(3)

                # Check for confirmation
                if self._check_success(page):
                    return True

            return False

        except Exception as e:
            print(f"Error filling form: {e}")
            return False

    def _find_field(self, page: Page, field_names: list) -> Optional[any]:
        """Find input field by various possible names"""
        for name in field_names:
            selectors = [
                f'input[name*="{name}"]',
                f'input[id*="{name}"]',
                f'input[placeholder*="{name}"]'
            ]

            for selector in selectors:
                try:
                    field = page.query_selector(selector)
                    if field and field.is_visible():
                        return field
                except:
                    continue

        return None

    def _fill_field(self, field, value: str):
        """Fill a form field with value"""
        try:
            field.click()
            field.fill(value)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error filling field: {e}")

    def _answer_screening_questions(self, page: Page, user_data: Dict):
        """Attempt to answer common screening questions"""
        # Look for yes/no questions
        yes_buttons = page.query_selector_all('button:has-text("Yes"), input[value="Yes"]')
        for button in yes_buttons[:3]:  # Answer first 3 yes/no questions
            try:
                if button.is_visible():
                    button.click()
                    time.sleep(0.5)
            except:
                continue

        # Look for text area questions (e.g., "Why do you want this job?")
        textareas = page.query_selector_all('textarea')
        for textarea in textareas[:2]:  # Fill first 2 text questions
            try:
                if textarea.is_visible():
                    default_answer = "I am excited about this opportunity and believe my skills align well with the position."
                    textarea.fill(default_answer)
                    time.sleep(0.5)
            except:
                continue

    def _find_submit_button(self, page: Page) -> Optional[any]:
        """Find the submit button"""
        selectors = [
            'button[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Apply")',
            'button:has-text("Send application")',
            'input[type="submit"]'
        ]

        for selector in selectors:
            try:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    return button
            except:
                continue

        return None

    def _check_success(self, page: Page) -> bool:
        """Check if application was successful"""
        success_indicators = [
            'text=Application sent',
            'text=Successfully applied',
            'text=Your application has been submitted',
            '.application-confirmation'
        ]

        for indicator in success_indicators:
            try:
                if page.query_selector(indicator):
                    return True
            except:
                continue

        return False


# Example usage
if __name__ == "__main__":
    user_info = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '555-123-4567'
    }

    job_url = "https://www.indeed.com/viewjob?jk=EXAMPLE_JOB_ID"
    resume_file = "../data/resumes/john_doe_resume.pdf"

    with IndeedApplicator(headless=False) as applicator:
        result = applicator.apply_to_job(job_url, user_info, resume_file)
        print(result)