from crewai.tools import BaseTool
import os
from dotenv import load_dotenv
import json
import scrapFly
import asyncio

class XScraper(BaseTool):
    name: str = "X handle scraper"
    description: str = "Search the X handle for the latest posts"

    def _run(self, url: str) -> str:
        try:
            # Check if the loop is already running
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            profile = loop.run_until_complete(scrapFly.scrape_profile(url))
        else:
            # Loop is already running; use asyncio.create_task and run it synchronously
            future = asyncio.ensure_future(scrapFly.scrape_profile(url))
            # Requires a way to wait without blocking — use asyncio-compatible structure
            import nest_asyncio
            nest_asyncio.apply()
            profile = loop.run_until_complete(future)

        profile_data = profile  # assuming `scrape_profile` already returns a dict
       
        return json.dumps(profile_data, indent=2)
