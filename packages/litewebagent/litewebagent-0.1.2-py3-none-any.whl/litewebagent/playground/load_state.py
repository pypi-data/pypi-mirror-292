import asyncio
from playwright.async_api import async_playwright
import json


async def load_login():
    terminated = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state='state.json')
        page = await context.new_page()
        await page.goto('https://clickup.com')

        print("Browser opened. Close the browser window to save the storage state.")

        async def save_storage_state(_):
            nonlocal terminated
            state = await context.storage_state()
            print('saving storage state', state)
            with open('state.json', 'w') as f:
                f.write(json.dumps(state, indent=4))
            await context.close()
            terminated = True

        page.on('close', save_storage_state)
        # Wait for the browser to close
        try:
            while not terminated:
                await asyncio.sleep(1)
            await browser.close()
        except KeyboardInterrupt:
            pass


asyncio.run(load_login())