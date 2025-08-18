#!/usr/bin/env python3
"""
GitHub Profile Viewer Script
View and interact with GitHub profile using Playwright
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


async def view_github_profile(username: str = "pr1m8", headless: bool = False, screenshot: bool = False):
    """
    View GitHub profile using Playwright
    
    Args:
        username: GitHub username to view (default: pr1m8)
        headless: Run browser in headless mode (default: False)
        screenshot: Take screenshot of profile (default: False)
    """
    profile_url = f"https://github.com/{username}"
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        try:
            print(f"📂 Navigating to {profile_url}")
            await page.goto(profile_url, wait_until="networkidle")
            
            # Wait for profile content to load
            await page.wait_for_selector('h1.vcard-names', timeout=10000)
            
            # Get profile information
            try:
                profile_name = await page.text_content('h1.vcard-names .p-name', timeout=5000)
                print(f"👤 Name: {profile_name}")
            except:
                print("👤 Name not found")
            
            try:
                bio = await page.text_content('.p-note.user-profile-bio div', timeout=5000)
                print(f"📝 Bio: {bio}")
            except:
                print("📝 Bio not found")
            
            # Count repositories
            try:
                repo_count = await page.text_content('[data-tab-item="repositories"] .Counter', timeout=5000)
                print(f"📚 Repositories: {repo_count}")
            except:
                print("📚 Repository count not found")
            
            print(f"✅ Profile loaded successfully!")
            
            # Take screenshot if requested
            if screenshot:
                # Create images directory if it doesn't exist
                images_dir = Path("images/screenshots")
                images_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = images_dir / f"{username}_profile_{timestamp}.png"
                
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
            
            if not headless:
                print("\n🔍 Browser window opened. Press Enter to close...")
                input()
            
        except Exception as e:
            print(f"❌ Error viewing profile: {e}")
            
        finally:
            await browser.close()


async def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(description="View GitHub profile with Playwright")
    parser.add_argument("--username", "-u", default="pr1m8", help="GitHub username")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--screenshot", "-s", action="store_true", help="Take screenshot")
    
    args = parser.parse_args()
    
    await view_github_profile(
        username=args.username,
        headless=args.headless,
        screenshot=args.screenshot
    )


if __name__ == "__main__":
    asyncio.run(main())