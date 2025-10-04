"""
End-to-end tests for user flows using Playwright
"""
import pytest
from playwright.async_api import async_playwright, Page, expect


@pytest.mark.e2e
@pytest.mark.asyncio
class TestUserAuthentication:
    """Test complete user authentication flow"""
    
    async def test_user_registration_flow(self):
        """Test complete user registration flow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to homepage
            await page.goto("http://localhost:3000")
            
            # Click register link
            await page.click('a[href="/register"]')
            await expect(page).to_have_url("http://localhost:3000/register")
            
            # Fill registration form
            await page.fill('input[type="email"]', "e2e@test.com")
            await page.fill('input[name="username"]', "e2euser")
            await page.fill('input[type="password"]', "E2EPassword123!")
            await page.fill('input[name="confirmPassword"]', "E2EPassword123!")
            
            # Submit form
            await page.click('button[type="submit"]')
            
            # Should redirect to dashboard
            await expect(page).to_have_url("http://localhost:3000/dashboard", timeout=5000)
            
            # Verify dashboard loaded
            await expect(page.locator('text="Welcome back"')).to_be_visible()
            
            await browser.close()
    
    async def test_login_logout_flow(self):
        """Test login and logout flow"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Go to login
            await page.goto("http://localhost:3000/login")
            
            # Fill login form
            await page.fill('input[type="text"]', "testuser")
            await page.fill('input[type="password"]', "TestPassword123!")
            
            # Submit
            await page.click('button[type="submit"]')
            
            # Wait for dashboard
            await expect(page).to_have_url("http://localhost:3000/dashboard", timeout=5000)
            
            # Logout
            await page.click('button:has-text("Logout")')
            
            # Should redirect to login
            await expect(page).to_have_url("http://localhost:3000/login")
            
            await browser.close()


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAudioUploadFlow:
    """Test complete audio upload and analysis flow"""
    
    async def test_upload_and_analyze_audio(self):
        """Test uploading and analyzing audio file"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Login first
            await page.goto("http://localhost:3000/login")
            await page.fill('input[type="text"]', "testuser")
            await page.fill('input[type="password"]', "TestPassword123!")
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/dashboard")
            
            # Navigate to upload page
            await page.click('a[href="/upload"]')
            await expect(page).to_have_url("http://localhost:3000/upload")
            
            # Upload file (using file chooser)
            async with page.expect_file_chooser() as fc_info:
                await page.click('input[type="file"]')
            file_chooser = await fc_info.value
            await file_chooser.set_files("tests/fixtures/test_120bpm_c_major.wav")
            
            # Wait for upload to complete
            await expect(page.locator('text="Complete"')).to_be_visible(timeout=30000)
            
            # Click to view results
            await page.click('button:has-text("View Results")')
            
            # Should show analysis results
            await expect(page.locator('text="Analysis Results"')).to_be_visible()
            
            await browser.close()


@pytest.mark.e2e
@pytest.mark.asyncio
class TestLibraryFlow:
    """Test library browsing flow"""
    
    async def test_browse_library(self):
        """Test browsing audio library"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Login
            await page.goto("http://localhost:3000/login")
            await page.fill('input[type="text"]', "testuser")
            await page.fill('input[type="password"]', "TestPassword123!")
            await page.click('button[type="submit"]')
            
            # Navigate to library
            await page.click('a[href="/library"]')
            await expect(page).to_have_url("http://localhost:3000/library")
            
            # Search for files
            await page.fill('input[placeholder*="Search"]', "test")
            
            # Wait for search results
            await page.wait_for_timeout(500)
            
            # Click on first file card
            await page.click('button:has-text("Details")').first
            
            # Modal should open
            await expect(page.locator('div[role="dialog"]')).to_be_visible()
            
            await browser.close()
