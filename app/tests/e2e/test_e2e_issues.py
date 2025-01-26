import re
from playwright.sync_api import Playwright, sync_playwright, expect
import pytest


@pytest.fixture()
def e2e_admin_login(playwright: Playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/")

    page.get_by_role("link", name="Login").click()
    page.get_by_placeholder("Enter email").click()
    page.get_by_placeholder("Enter email").fill("admintest@test.com")
    page.get_by_placeholder("Enter email").press("Tab")
    page.get_by_placeholder("Enter password").fill("test1A$c34")
    page.get_by_placeholder("Enter password").press("Enter")

    yield page

    browser.close()


def test_e2e_create_issue(e2e_admin_login: Playwright):
    page = e2e_admin_login
    page.get_by_label("Select an issue type").select_option("Bug")
    page.get_by_placeholder("What issue are you having ?").click()
    page.get_by_placeholder("What issue are you having ?").fill("creating an issue")
    page.get_by_placeholder("What issue are you having ?").press("Tab")
    page.get_by_placeholder("Add more detail about the").fill("e2e create issue test")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Successfully created issue")).to_be_visible()
