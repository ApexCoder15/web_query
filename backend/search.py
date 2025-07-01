import asyncio
from playwright.async_api import async_playwright

async def screenshot_result(query: str, link_number: int, img_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False for debugging

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        search_url = f"https://lite.duckduckgo.com/lite/?q={query.replace(' ', '+')}"
        await page.goto(search_url)

        for i in range(6+link_number):
            await page.keyboard.press("Tab")
            #await asyncio.sleep(1)
        await page.keyboard.press("Enter")       


        # Save screenshot for debugging
        await page.screenshot(path=img_path, full_page=True)
        await browser.close()


# Run and print part of result
# if __name__ == "__main__":
#     asyncio.run(screenshot_result("langchain", 2, "sc.png"))







